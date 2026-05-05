"""
DocumentLoader: carrega arquivos PDF, DOCX e TXT de um diretório para ingestão.

Suporta:
- Arquivos .pdf via pdfplumber (extração de texto) + GPT Vision OCR para
  páginas com pouco texto mas com imagens (screenshots de interface, etc.)
- Arquivos .docx via python-docx (parágrafos + tabelas) + GPT Vision OCR
  para imagens embutidas no documento
- Arquivos .txt via leitura direta UTF-8

Páginas/imagens com texto insuficiente são enviadas ao GPT Vision para
transcrição do conteúdo visual.

Arquivos ilegíveis são registrados em log e ignorados (sem lançar exceção).
"""

import base64
import io
import logging
import os
import time
from collections.abc import Iterator
from pathlib import Path

import pdfplumber
from docx import Document as DocxDocument
from openai import OpenAI

from app.models import ChunkMetadata

logger = logging.getLogger(__name__)

# Número mínimo de caracteres de texto extraído para considerar que a página
# não precisa de OCR. Páginas abaixo desse limiar com imagens serão enviadas
# ao GPT Vision.
OCR_MIN_CHARS = 200

# Se True, aplica OCR em TODAS as páginas com imagens, mesmo que já tenham
# texto suficiente. Útil para PDFs com screenshots de interface.
OCR_ALL_IMAGES = True

# Modelo GPT Vision usado para transcrição de imagens
OCR_MODEL = "gpt-4o-mini"

# Prompt enviado ao GPT Vision para transcrição
OCR_SYSTEM_PROMPT = (
    "Você é um assistente especializado em transcrição de documentos técnicos. "
    "Extraia e transcreva TODO o texto visível nesta imagem de página de documento, "
    "incluindo textos em campos de formulário, botões, menus, tabelas e capturas de tela "
    "de interface. Preserve a estrutura e hierarquia do conteúdo. "
    "Responda APENAS com o texto transcrito, sem comentários adicionais."
)


def _get_ocr_client() -> OpenAI | None:
    """Retorna um cliente OpenAI síncrono para OCR, ou None se a chave não estiver disponível."""
    api_key = os.environ.get("LLM_API_KEY")
    if not api_key:
        try:
            from app.config import settings  # noqa: PLC0415
            api_key = settings.LLM_API_KEY
        except Exception:  # noqa: BLE001
            return None
    return OpenAI(api_key=api_key)


def _find_poppler_path() -> str | None:
    """
    Tenta localizar o Poppler no Windows em caminhos comuns de instalação.
    Retorna None se não encontrado (pdf2image tentará usar o PATH).
    """
    import shutil  # noqa: PLC0415

    if shutil.which("pdftoppm"):
        return None

    winget_base = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Packages"
    if winget_base.exists():
        for candidate in winget_base.rglob("pdftoppm.exe"):
            return str(candidate.parent)

    for path in [Path("C:/Program Files/poppler/bin"), Path("C:/poppler/bin")]:
        if path.exists() and (path / "pdftoppm.exe").exists():
            return str(path)

    return None


def _page_to_base64(pdf_path: Path, page_number: int, dpi: int = 150) -> str | None:
    """Converte uma página do PDF em imagem PNG codificada em base64."""
    try:
        from pdf2image import convert_from_path  # noqa: PLC0415

        images = convert_from_path(
            str(pdf_path),
            first_page=page_number,
            last_page=page_number,
            dpi=dpi,
            poppler_path=_find_poppler_path(),
        )
        if not images:
            return None

        buffer = io.BytesIO()
        images[0].save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    except Exception as exc:  # noqa: BLE001
        logger.warning("Não foi possível converter página %d para imagem: %s", page_number, exc)
        return None


def _call_vision(
    ocr_client: OpenAI,
    image_b64: str,
    mime: str,
    label: str,
    token_counter: dict,
) -> str:
    """Envia uma imagem em base64 ao GPT Vision e retorna o texto transcrito."""
    try:
        response = ocr_client.chat.completions.create(
            model=OCR_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": OCR_SYSTEM_PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime};base64,{image_b64}",
                                "detail": "high",
                            },
                        },
                    ],
                }
            ],
            max_tokens=2048,
        )
        if response.usage:
            token_counter["prompt_tokens"] += response.usage.prompt_tokens
            token_counter["completion_tokens"] += response.usage.completion_tokens
            token_counter["total_tokens"] += response.usage.total_tokens

        transcribed = response.choices[0].message.content or ""
        logger.info("OCR '%s': %d caracteres transcritos.", label, len(transcribed))
        # Pausa para respeitar o rate limit de tokens/minuto da API Vision
        time.sleep(1.0)
        return transcribed

    except Exception as exc:  # noqa: BLE001
        logger.error("Erro no OCR GPT Vision de '%s': %s", label, exc)
        return ""


def _ocr_pdf_page(
    ocr_client: OpenAI,
    pdf_path: Path,
    page_number: int,
    token_counter: dict,
) -> str:
    """Usa GPT Vision para transcrever uma página inteira do PDF."""
    logger.info("OCR via GPT Vision na página %d de '%s'...", page_number, pdf_path.name)
    image_b64 = _page_to_base64(pdf_path, page_number)
    if not image_b64:
        logger.warning("Não foi possível gerar imagem para OCR da página %d.", page_number)
        return ""
    return _call_vision(
        ocr_client, image_b64, "image/png",
        f"{pdf_path.name}::p{page_number}", token_counter,
    )


def _ocr_image_bytes(
    ocr_client: OpenAI,
    image_bytes: bytes,
    image_name: str,
    token_counter: dict,
) -> str:
    """Usa GPT Vision para transcrever uma imagem fornecida como bytes."""
    try:
        if image_bytes[:4] == b'\x89PNG':
            mime = "image/png"
        elif image_bytes[:2] == b'\xff\xd8':
            mime = "image/jpeg"
        elif image_bytes[:4] in (b'GIF8', b'GIF9'):
            mime = "image/gif"
        else:
            from PIL import Image  # noqa: PLC0415
            img = Image.open(io.BytesIO(image_bytes))
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            image_bytes = buf.getvalue()
            mime = "image/png"

        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        return _call_vision(ocr_client, image_b64, mime, image_name, token_counter)

    except Exception as exc:  # noqa: BLE001
        logger.error("Erro ao preparar imagem '%s' para OCR: %s", image_name, exc)
        return ""


class DocumentLoader:
    """
    Carrega arquivos PDF, DOCX e TXT de um diretório, produzindo pares
    (text, metadata) para cada unidade de texto extraída.

    Para PDFs, páginas com pouco texto extraível mas com imagens são
    automaticamente transcritas via GPT Vision (OCR).

    Para DOCX, parágrafos e tabelas são extraídos diretamente; imagens
    embutidas são transcritas via GPT Vision quando OCR está ativado.

    Atributo público:
        ocr_token_usage (dict): Tokens consumidos pelo OCR GPT Vision.
            Chaves: 'prompt_tokens', 'completion_tokens', 'total_tokens'.
    """

    def __init__(self, ocr_enabled: bool = True) -> None:
        """
        Args:
            ocr_enabled: Se True, ativa o OCR via GPT Vision. Padrão: True.
        """
        self._ocr_enabled = ocr_enabled
        self._ocr_client: OpenAI | None = None
        self.ocr_token_usage: dict = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        }

        if ocr_enabled:
            self._ocr_client = _get_ocr_client()
            if self._ocr_client is None:
                logger.warning("OCR desativado: LLM_API_KEY não encontrada no ambiente.")

    def load_directory(self, directory: Path) -> Iterator[tuple[str, ChunkMetadata]]:
        """
        Carrega todos os arquivos PDF, DOCX e TXT do diretório informado.

        Para PDFs: itera página a página; páginas com texto insuficiente e
        imagens são transcritas via OCR.

        Para DOCX: extrai parágrafos, tabelas e imagens embutidas (OCR).

        Para TXTs: lê o arquivo inteiro como uma única string.

        Yields:
            Tuplas (text, metadata) para cada unidade de texto extraída.
        """
        supported_extensions = {".pdf", ".docx", ".txt"}

        for file_path in sorted(directory.iterdir()):
            if not file_path.is_file():
                continue

            suffix = file_path.suffix.lower()
            if suffix not in supported_extensions:
                logger.warning("Formato não suportado, ignorando arquivo: %s", file_path.name)
                continue

            if suffix == ".pdf":
                yield from self._load_pdf(file_path)
            elif suffix == ".docx":
                yield from self._load_docx(file_path)
            elif suffix == ".txt":
                yield from self._load_txt(file_path)

    def _load_pdf(self, file_path: Path) -> Iterator[tuple[str, ChunkMetadata]]:
        """Extrai texto de um PDF página a página, com OCR para páginas com imagens."""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page_index, page in enumerate(pdf.pages):
                    page_number = page_index + 1
                    try:
                        text = page.extract_text() or ""
                        has_images = len(page.images) > 0
                        needs_ocr = (
                            self._ocr_enabled
                            and self._ocr_client is not None
                            and has_images
                            and (OCR_ALL_IMAGES or len(text.strip()) < OCR_MIN_CHARS)
                        )

                        if needs_ocr:
                            logger.info(
                                "Página %d de '%s': %d imagem(ns) — aplicando OCR%s.",
                                page_number, file_path.name, len(page.images),
                                " (texto insuficiente)" if len(text.strip()) < OCR_MIN_CHARS else "",
                            )
                            ocr_text = _ocr_pdf_page(
                                self._ocr_client,  # type: ignore[arg-type]
                                file_path, page_number, self.ocr_token_usage,
                            )
                            # Combina texto extraído + OCR preservando ambos
                            combined = "\n\n".join(
                                t for t in [text.strip(), ocr_text.strip()] if t
                            )
                            text = combined if combined else text

                        if not text.strip():
                            logger.debug(
                                "Página %d de '%s' sem texto após extração/OCR — ignorando.",
                                page_number, file_path.name,
                            )
                            continue

                        yield text, ChunkMetadata(
                            filename=file_path.name,
                            page=page_number,
                            position=page_index,
                            chunk_index=0,
                        )

                    except Exception as exc:  # noqa: BLE001
                        logger.error(
                            "Erro ao extrair página %d do arquivo '%s': %s",
                            page_number, file_path.name, exc,
                        )
        except Exception as exc:  # noqa: BLE001
            logger.error("Erro ao abrir arquivo PDF '%s': %s", file_path.name, exc)

    def _load_docx(self, file_path: Path) -> Iterator[tuple[str, ChunkMetadata]]:
        """
        Extrai texto de um arquivo DOCX.

        Combina parágrafos, tabelas e transcrições OCR de imagens embutidas
        em uma única string, preservando a ordem de aparição no documento.
        """
        try:
            from docx.oxml.ns import qn  # noqa: PLC0415

            doc = DocxDocument(str(file_path))
            parts: list[str] = []
            image_index = 0

            # Mapa rId → bytes da imagem
            image_map: dict[str, bytes] = {}
            for rel in doc.part.rels.values():
                if "image" in rel.reltype:
                    try:
                        image_map[rel.rId] = rel.target_part.blob
                    except Exception:  # noqa: BLE001
                        pass

            for block in doc.element.body:
                tag = block.tag.split("}")[-1] if "}" in block.tag else block.tag

                if tag == "p":
                    # Texto do parágrafo
                    text = "".join(
                        node.text or ""
                        for node in block.iter()
                        if node.tag == qn("w:t")
                    )
                    if text.strip():
                        parts.append(text)

                    # Imagens embutidas no parágrafo
                    if self._ocr_enabled and self._ocr_client is not None:
                        for blip in block.iter(qn("a:blip")):
                            r_embed = blip.get(qn("r:embed"))
                            if r_embed and r_embed in image_map:
                                image_index += 1
                                img_name = f"{file_path.name}::imagem_{image_index}"
                                logger.info(
                                    "DOCX '%s': aplicando OCR na imagem %d...",
                                    file_path.name, image_index,
                                )
                                ocr_text = _ocr_image_bytes(
                                    self._ocr_client,  # type: ignore[arg-type]
                                    image_map[r_embed],
                                    img_name,
                                    self.ocr_token_usage,
                                )
                                if ocr_text.strip():
                                    parts.append(f"[Imagem {image_index}]\n{ocr_text.strip()}")

                elif tag == "tbl":
                    # Tabela
                    rows: list[str] = []
                    for tr in block.findall(f".//{qn('w:tr')}"):
                        cells: list[str] = []
                        for tc in tr.findall(f".//{qn('w:tc')}"):
                            cell_text = "".join(
                                node.text or ""
                                for node in tc.iter()
                                if node.tag == qn("w:t")
                            )
                            cells.append(cell_text.strip())
                        if any(cells):
                            rows.append("\t".join(cells))
                    if rows:
                        parts.append("\n".join(rows))

            text = "\n\n".join(parts)
            if not text.strip():
                logger.warning("Arquivo DOCX '%s' não contém texto extraível.", file_path.name)
                return

            if image_index > 0:
                logger.info(
                    "DOCX '%s': %d imagem(ns) processada(s) via OCR.",
                    file_path.name, image_index,
                )

            yield text, ChunkMetadata(
                filename=file_path.name,
                page=None,
                position=0,
                chunk_index=0,
            )

        except Exception as exc:  # noqa: BLE001
            logger.error("Erro ao ler arquivo DOCX '%s': %s", file_path.name, exc)

    def _load_txt(self, file_path: Path) -> Iterator[tuple[str, ChunkMetadata]]:
        """Lê um arquivo TXT inteiro como uma única string."""
        try:
            text = file_path.read_text(encoding="utf-8")
            yield text, ChunkMetadata(
                filename=file_path.name,
                page=None,
                position=0,
                chunk_index=0,
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("Erro ao ler arquivo TXT '%s': %s", file_path.name, exc)
