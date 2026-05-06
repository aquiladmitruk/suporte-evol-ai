import sys
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv('.env')

import asyncio
from app.config import settings
from app.embedding_service import EmbeddingService
from qdrant_client import AsyncQdrantClient

async def test():
    embed = EmbeddingService(
        model=settings.EMBEDDING_MODEL,
        api_key=settings.LLM_API_KEY,
        dimensions=settings.EMBEDDING_DIMENSIONS,
    )
    client = AsyncQdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)

    print('Colecao:', settings.QDRANT_COLLECTION)
    print('Threshold:', settings.RAG_SIMILARITY_THRESHOLD)
    print('Dimensions:', settings.EMBEDDING_DIMENSIONS)

    vector = await embed.embed('como emitir boleto')
    print('Dimensao do vetor gerado:', len(vector))

    results = await client.search(
        collection_name=settings.QDRANT_COLLECTION,
        query_vector=vector,
        limit=5,
    )
    print('Resultados (sem threshold):', len(results))
    for r in results:
        p = r.payload or {}
        arquivo = p.get('source_file') or p.get('filename') or '?'
        texto = p.get('original_text') or p.get('content') or '?'
        print(f'  score={r.score:.4f} | arquivo={arquivo} | texto={str(texto)[:80]}')

    await client.close()

asyncio.run(test())
