"""Remove todos os pontos de um arquivo específico da coleção Qdrant."""
from dotenv import load_dotenv
load_dotenv(".env")
import asyncio, sys
sys.path.insert(0, ".")
from app.config import settings
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, PayloadSchemaType

async def delete(filename: str):
    client = AsyncQdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)

    # Cria índice keyword no campo filename (necessário para filtro)
    await client.create_payload_index(
        collection_name=settings.QDRANT_COLLECTION,
        field_name="filename",
        field_schema=PayloadSchemaType.KEYWORD,
    )
    print("Índice 'filename' criado/confirmado.")

    result = await client.delete(
        collection_name=settings.QDRANT_COLLECTION,
        points_selector=Filter(
            must=[FieldCondition(key="filename", match=MatchValue(value=filename))]
        ),
    )
    print(f"Pontos de '{filename}' removidos. Status: {result.status}")
    info = await client.get_collection(settings.QDRANT_COLLECTION)
    print(f"Total de pontos restantes: {info.points_count}")
    await client.close()

asyncio.run(delete("Api_Inter.pdf"))
