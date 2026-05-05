"""Remove chunks de um arquivo e reingeriu só ele."""
from dotenv import load_dotenv
load_dotenv(".env")
import asyncio, sys, hashlib, uuid
sys.path.insert(0, ".")
from pathlib import Path
from app.config import settings
from app.embedding_service import EmbeddingService
from scripts.document_loader import DocumentLoader
from scripts.text_chunker import TextChunker
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, PayloadSchemaType, PointStruct

TARGET = "imagens_tray.pdf"
INPUT_DIR = Path("documents")

def chunk_id(content: str) -> str:
    digest = hashlib.sha256(content.encode()).hexdigest()
    return str(uuid.UUID(digest[:32]))

async def run():
    client = AsyncQdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)

    # Garante índice e remove chunks antigos
    await client.create_payload_index(
        collection_name=settings.QDRANT_COLLECTION,
        field_name="filename",
        field_schema=PayloadSchemaType.KEYWORD,
    )
    result = await client.delete(
        collection_name=settings.QDRANT_COLLECTION,
        points_selector=Filter(must=[FieldCondition(key="filename", match=MatchValue(value=TARGET))])
    )
    print(f"Chunks antigos removidos: {result.status}")

    # Reingerir
    embed = EmbeddingService(model=settings.EMBEDDING_MODEL, api_key=settings.LLM_API_KEY)
    chunker = TextChunker(chunk_size=settings.CHUNK_SIZE, chunk_overlap=settings.CHUNK_OVERLAP)
    loader = DocumentLoader(ocr_enabled=True)

    chunks_saved = 0
    for text, metadata in loader.load_directory(INPUT_DIR):
        if metadata.filename != TARGET:
            continue
        for chunk in chunker.chunk(text, metadata):
            vector = await embed.embed(chunk.content)
            await client.upsert(
                collection_name=settings.QDRANT_COLLECTION,
                points=[PointStruct(
                    id=chunk_id(chunk.content),
                    vector=vector,
                    payload={
                        "content": chunk.content,
                        "filename": chunk.metadata.filename,
                        "page": chunk.metadata.page,
                        "position": chunk.metadata.position,
                        "chunk_index": chunk.metadata.chunk_index,
                    }
                )]
            )
            chunks_saved += 1
            print(f"  Chunk salvo: p{chunk.metadata.page} | {chunk.content[:80]}...")

    print(f"\nTotal chunks salvos: {chunks_saved}")
    print(f"OCR tokens usados: {loader.ocr_token_usage}")
    await client.close()

asyncio.run(run())
