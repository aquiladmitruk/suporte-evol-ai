"""
Router de documentos para o Assistente de IA do ERP Evol.

Expõe os endpoints:
  GET /api/documents           — lista arquivos disponíveis para download
  GET /api/documents/{filename} — serve um arquivo para download
"""

import logging
import mimetypes
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()

# Pasta de documentos relativa à raiz do backend
DOCUMENTS_DIR = Path(__file__).parent.parent.parent / "documents"


class DocumentoItem(BaseModel):
    """Representa um arquivo disponível para download."""

    filename: str
    size_bytes: int


@router.get("/documents", response_model=list[DocumentoItem])
async def list_documents() -> list[DocumentoItem]:
    """
    Lista os arquivos disponíveis na pasta documents/.

    Returns:
        Lista de DocumentoItem ordenada alfabeticamente.
        Retorna lista vazia se a pasta não existir ou estiver vazia.
    """
    if not DOCUMENTS_DIR.exists() or not DOCUMENTS_DIR.is_dir():
        return []

    items: list[DocumentoItem] = []
    for entry in sorted(DOCUMENTS_DIR.iterdir()):
        # Ignorar subdiretórios e arquivos ocultos (.gitkeep, etc.)
        if entry.is_file() and not entry.name.startswith("."):
            items.append(DocumentoItem(filename=entry.name, size_bytes=entry.stat().st_size))

    return items


@router.get("/documents/{filename}")
async def download_document(filename: str) -> FileResponse:
    """
    Serve um arquivo da pasta documents/ para download.

    Args:
        filename: Nome do arquivo a ser baixado.

    Returns:
        FileResponse com o conteúdo do arquivo e cabeçalhos de download.

    Raises:
        HTTPException 400: Se o filename contiver sequências de path traversal.
        HTTPException 404: Se o arquivo não existir na pasta documents/.
    """
    # Proteção contra path traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(
            status_code=400,
            detail="Nome de arquivo inválido.",
        )

    file_path = DOCUMENTS_DIR / filename

    # Verificar se o arquivo existe e está dentro da pasta correta
    try:
        resolved = file_path.resolve()
        documents_resolved = DOCUMENTS_DIR.resolve()
        if not str(resolved).startswith(str(documents_resolved)):
            raise HTTPException(status_code=400, detail="Nome de arquivo inválido.")
    except Exception:
        raise HTTPException(status_code=400, detail="Nome de arquivo inválido.")

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail=f"Arquivo '{filename}' não encontrado.",
        )

    # Detectar tipo MIME pela extensão
    media_type, _ = mimetypes.guess_type(filename)
    if media_type is None:
        media_type = "application/octet-stream"

    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=filename,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
