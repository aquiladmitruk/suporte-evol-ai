"""
Script de migração: recria a coleção Qdrant com vetores de 1536 dimensões
(text-embedding-3-small, padrão OpenAI) a partir dos textos já armazenados
no payload de cada ponto.

Fluxo:
1. Lê todos os pontos da coleção atual em lotes (scroll)
2. Recria a coleção com dimensão 1536 e distância Cosine
3. Para cada lote, gera novos embeddings via API OpenAI e faz upsert

Uso (a partir de backend/):
    python scripts/migrate_embeddings.py

Variáveis de ambiente necessárias (lidas do .env):
    QDRANT_URL, QDRANT_API_KEY, LLM_API_KEY
    QDRANT_COLLECTION (padrão: documents)
"""

import asyncio
import logging
import sys
from pathlib import Path

# Garante que o pacote backend está no path ao rodar como script
_BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from dotenv import load_dotenv
load_dotenv(_BACKEND_DIR / ".env")

from openai import AsyncOpenAI
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# Dimensão alvo — text-embedding-3-small nativo (sem redução)
TARGET_DIMENSIONS = 1536
EMBEDDING_MODEL = "text-embedding-3-small"
BATCH_SIZE = 50  # pontos por lote (respeita rate limit da API)


async def migrate() -> None:
    qdrant = AsyncQdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)
    openai = AsyncOpenAI(api_key=settings.LLM_API_KEY)
    collection = settings.QDRANT_COLLECTION

    # ------------------------------------------------------------------
    # 1. Contar pontos existentes
    # ------------------------------------------------------------------
    info = await qdrant.get_collection(collection)
    total = info.points_count
    logger.info("Coleção '%s': %d pontos com %dd → migrando para %dd",
                collection, total,
                info.config.params.vectors.size,  # type: ignore[union-attr]
                TARGET_DIMENSIONS)

    # ------------------------------------------------------------------
    # 2. Recriar coleção com nova dimensão
    #    Renomeia a antiga para backup, cria nova com mesmo nome
    # ------------------------------------------------------------------
    backup_name = f"{collection}_backup_384d"
    existing = {c.name for c in (await qdrant.get_collections()).collections}

    if backup_name in existing:
        logger.info("Backup '%s' já existe — pulando criação do backup.", backup_name)
    else:
        logger.info("Criando backup '%s'...", backup_name)
        await qdrant.create_collection(
            collection_name=backup_name,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )
        # Copia todos os pontos (com vetores) para o backup
        offset = None
        copied = 0
        while True:
            scroll_result = await qdrant.scroll(
                collection_name=collection,
                limit=BATCH_SIZE,
                offset=offset,
                with_payload=True,
                with_vectors=True,
            )
            points, offset = scroll_result
            if not points:
                break
            await qdrant.upsert(
                collection_name=backup_name,
                points=[
                    PointStruct(id=p.id, vector=p.vector, payload=p.payload)  # type: ignore[arg-type]
                    for p in points
                ],
            )
            copied += len(points)
            logger.info("Backup: %d/%d pontos copiados", copied, total)
            if offset is None:
                break
        logger.info("Backup concluído: %d pontos em '%s'.", copied, backup_name)

    # ------------------------------------------------------------------
    # 3. Recriar coleção principal com 1536d
    # ------------------------------------------------------------------
    logger.info("Recriando coleção '%s' com %dd...", collection, TARGET_DIMENSIONS)
    await qdrant.delete_collection(collection)
    await qdrant.create_collection(
        collection_name=collection,
        vectors_config=VectorParams(size=TARGET_DIMENSIONS, distance=Distance.COSINE),
    )

    # ------------------------------------------------------------------
    # 4. Ler pontos do backup, gerar novos embeddings e fazer upsert
    # ------------------------------------------------------------------
    offset = None
    processed = 0
    skipped = 0

    while True:
        scroll_result = await qdrant.scroll(
            collection_name=backup_name,
            limit=BATCH_SIZE,
            offset=offset,
            with_payload=True,
            with_vectors=False,
        )
        points, offset = scroll_result
        if not points:
            break

        # Filtra pontos que têm texto
        valid = [(p.id, p.payload) for p in points
                 if p.payload and p.payload.get("original_text", "").strip()]
        skipped += len(points) - len(valid)

        if valid:
            texts = [payload["original_text"] for _, payload in valid]

            # Gera embeddings em batch
            response = await openai.embeddings.create(
                model=EMBEDDING_MODEL,
                input=texts,
            )
            vectors = [item.embedding for item in sorted(response.data, key=lambda x: x.index)]

            new_points = [
                PointStruct(id=point_id, vector=vector, payload=payload)
                for (point_id, payload), vector in zip(valid, vectors)
            ]
            await qdrant.upsert(collection_name=collection, points=new_points)

        processed += len(valid)
        logger.info("Progresso: %d/%d pontos migrados (ignorados sem texto: %d)",
                    processed, total, skipped)

        if offset is None:
            break

    # ------------------------------------------------------------------
    # 5. Relatório final
    # ------------------------------------------------------------------
    info_new = await qdrant.get_collection(collection)
    logger.info(
        "Migração concluída!\n"
        "  Pontos migrados : %d\n"
        "  Pontos ignorados: %d (sem original_text)\n"
        "  Dimensão nova   : %d\n"
        "  Backup mantido  : '%s'",
        processed, skipped,
        info_new.config.params.vectors.size,  # type: ignore[union-attr]
        backup_name,
    )

    await qdrant.close()


if __name__ == "__main__":
    asyncio.run(migrate())
