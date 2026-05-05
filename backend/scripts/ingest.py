"""
Script de ingestão de documentos para o Assistente de IA do ERP Evol.

Uso:
    python scripts/ingest.py --input-dir /caminho/para/docs [--collection evol_docs]

Fluxo:
1. Carrega configurações via app.config.settings
2. Instancia EmbeddingService, AsyncQdrantClient, TextChunker, DocumentLoader
3. Garante que a coleção existe no Qdrant (cria se necessário)
4. Para cada (text, metadata) do DocumentLoader:
   a. Chunkeia o texto via TextChunker
   b. Gera embedding para cada chunk via EmbeddingService
   c. Calcula ID do ponto como UUID derivado de SHA-256 do conteúdo
   d. Faz upsert no Qdrant
5. Exibe relatório final: arquivos processados, chunks gerados, erros e uso de tokens
"""

import argparse
import asyncio
import hashlib
import logging
import sys
import uuid
from pathlib import Path

from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

# Ensure the backend package root is on sys.path when running as a script
_SCRIPT_DIR = Path(__file__).resolve().parent
_BACKEND_DIR = _SCRIPT_DIR.parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

# Carrega .env antes de importar settings (necessário ao rodar como script)
from dotenv import load_dotenv  # noqa: E402
load_dotenv(_BACKEND_DIR / ".env")

from app.config import settings  # noqa: E402
from app.embedding_service import EmbeddingService  # noqa: E402
from scripts.document_loader import DocumentLoader  # noqa: E402
from scripts.text_chunker import TextChunker  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Preços por 1 000 tokens (USD) — atualize conforme tabela OpenAI
_PRICING: dict[str, dict[str, float]] = {
    "text-embedding-3-small": {"input": 0.00002, "output": 0.0},
    "text-embedding-3-large": {"input": 0.00013, "output": 0.0},
    "text-embedding-ada-002":  {"input": 0.00010, "output": 0.0},
    # GPT Vision (OCR)
    "gpt-4o-mini": {"input": 0.000150, "output": 0.000600},
    "gpt-4o":      {"input": 0.005000, "output": 0.015000},
}

_USD_TO_BRL = 5.75  # taxa de câmbio aproximada


def _estimate_cost(model: str, prompt_tokens: int, completion_tokens: int = 0) -> float:
    """Estima o custo em USD para um dado modelo e quantidade de tokens."""
    pricing = _PRICING.get(model)
    if not pricing:
        return 0.0
    cost = (prompt_tokens / 1_000) * pricing["input"]
    cost += (completion_tokens / 1_000) * pricing["output"]
    return cost


def _chunk_id(content: str) -> str:
    """Deriva um UUID determinístico a partir do SHA-256 do conteúdo do chunk."""
    digest = hashlib.sha256(content.encode()).hexdigest()
    return str(uuid.UUID(digest[:32]))


async def _ensure_collection(
    client: AsyncQdrantClient,
    collection_name: str,
    vector_size: int,
) -> None:
    """Cria a coleção no Qdrant se ela ainda não existir."""
    existing = await client.get_collections()
    existing_names = {c.name for c in existing.collections}
    if collection_name not in existing_names:
        logger.info("Criando coleção '%s' com dimensão %d...", collection_name, vector_size)
        await client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )
    else:
        logger.info("Coleção '%s' já existe.", collection_name)


async def run_ingestion(input_dir: Path, collection_name: str) -> None:
    """Executa o pipeline completo de ingestão."""
    embedding_service = EmbeddingService(
        model=settings.EMBEDDING_MODEL,
        api_key=settings.LLM_API_KEY,
    )
    qdrant_kwargs: dict = {"url": settings.QDRANT_URL}
    if settings.QDRANT_API_KEY:
        qdrant_kwargs["api_key"] = settings.QDRANT_API_KEY
    qdrant_client = AsyncQdrantClient(**qdrant_kwargs)

    chunker = TextChunker(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
    )
    loader = DocumentLoader()

    logger.info("Determinando dimensão do modelo de embeddings...")
    sample_vector = await embedding_service.embed("dimensão")
    vector_size = len(sample_vector)
    logger.info("Dimensão do vetor: %d", vector_size)

    await _ensure_collection(qdrant_client, collection_name, vector_size)

    files_processed = 0
    chunks_generated = 0
    errors = 0
    current_file: str | None = None

    try:
        for text, metadata in loader.load_directory(input_dir):
            file_name = metadata.filename

            if file_name != current_file:
                if current_file is not None:
                    files_processed += 1
                current_file = file_name
                logger.info("Processando arquivo: %s", file_name)

            try:
                chunks = chunker.chunk(text, metadata)
                for chunk in chunks:
                    try:
                        vector = await embedding_service.embed(chunk.content)
                        point_id = _chunk_id(chunk.content)
                        point = PointStruct(
                            id=point_id,
                            vector=vector,
                            payload={
                                "content": chunk.content,
                                "filename": chunk.metadata.filename,
                                "page": chunk.metadata.page,
                                "position": chunk.metadata.position,
                                "chunk_index": chunk.metadata.chunk_index,
                            },
                        )
                        await qdrant_client.upsert(
                            collection_name=collection_name,
                            points=[point],
                        )
                        chunks_generated += 1
                    except Exception as exc:  # noqa: BLE001
                        logger.error(
                            "Erro ao gerar embedding/upsert para chunk do arquivo '%s': %s",
                            file_name,
                            exc,
                        )
                        errors += 1
            except Exception as exc:  # noqa: BLE001
                logger.error(
                    "Erro ao processar arquivo '%s': %s", file_name, exc
                )
                errors += 1

    except Exception as exc:  # noqa: BLE001
        logger.error("Erro fatal durante a ingestão: %s", exc)
        errors += 1

    if current_file is not None:
        files_processed += 1

    # -----------------------------------------------------------------------
    # Cálculo de custos
    # -----------------------------------------------------------------------
    embed_tokens = embedding_service.total_tokens_used
    embed_cost_usd = _estimate_cost(settings.EMBEDDING_MODEL, embed_tokens)

    ocr = loader.ocr_token_usage
    ocr_model = "gpt-4o-mini"  # deve bater com OCR_MODEL em document_loader.py
    ocr_cost_usd = _estimate_cost(
        ocr_model,
        ocr["prompt_tokens"],
        ocr["completion_tokens"],
    )

    total_cost_usd = embed_cost_usd + ocr_cost_usd
    total_cost_brl = total_cost_usd * _USD_TO_BRL

    # -----------------------------------------------------------------------
    # Relatório final
    # -----------------------------------------------------------------------
    sep = "=" * 54
    print(f"\n{sep}")
    print("RELATÓRIO DE INGESTÃO")
    print(sep)
    print(f"  Arquivos processados       : {files_processed}")
    print(f"  Chunks gerados             : {chunks_generated}")
    print(f"  Erros encontrados          : {errors}")
    print(sep)
    print("CONSUMO DE TOKENS")
    print(sep)
    print(f"  Embeddings ({settings.EMBEDDING_MODEL})")
    print(f"    Tokens                   : {embed_tokens:,}")
    print(f"    Custo estimado           : U$ {embed_cost_usd:.6f}")
    print()
    print(f"  OCR / GPT Vision ({ocr_model})")
    print(f"    Tokens de entrada        : {ocr['prompt_tokens']:,}")
    print(f"    Tokens de saída          : {ocr['completion_tokens']:,}")
    print(f"    Total tokens OCR         : {ocr['total_tokens']:,}")
    print(f"    Custo estimado           : U$ {ocr_cost_usd:.6f}")
    print(sep)
    print(f"  TOTAL TOKENS               : {embed_tokens + ocr['total_tokens']:,}")
    print(f"  CUSTO TOTAL (USD)          : U$ {total_cost_usd:.6f}")
    print(f"  CUSTO TOTAL (BRL ~R${_USD_TO_BRL})  : R$ {total_cost_brl:.6f}")
    print(sep)

    await qdrant_client.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ingere documentos PDF e TXT no banco vetorial Qdrant."
    )
    parser.add_argument(
        "--input-dir",
        required=True,
        type=Path,
        help="Diretório contendo os arquivos de documentação (PDF e TXT).",
    )
    parser.add_argument(
        "--collection",
        default=settings.QDRANT_COLLECTION,
        help="Nome da coleção no Qdrant (padrão: %(default)s).",
    )
    args = parser.parse_args()

    if not args.input_dir.is_dir():
        logger.error("O diretório informado não existe: %s", args.input_dir)
        sys.exit(1)

    asyncio.run(run_ingestion(args.input_dir, args.collection))


if __name__ == "__main__":
    main()
