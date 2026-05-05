"""
Serviço de busca semântica (RAG) para o Assistente de IA do ERP Evol.

Usa o Qdrant como banco vetorial para recuperar chunks relevantes
com base na similaridade semântica da query do usuário.
"""

from app.embedding_service import EmbeddingService
from app.models import RetrievedChunk, SourceReference


class RAGService:
    """
    Executa a busca semântica no banco vetorial Qdrant.

    Args:
        embedding_service: Serviço responsável por gerar embeddings de texto.
        vector_db_client: Cliente assíncrono do Qdrant (AsyncQdrantClient).
        top_k: Número máximo de chunks a recuperar por busca.
        similarity_threshold: Score mínimo de similaridade para incluir um chunk.
        collection_name: Nome da coleção no Qdrant onde os chunks estão indexados.
    """

    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_db_client,  # qdrant_client.AsyncQdrantClient
        top_k: int,
        similarity_threshold: float,
        collection_name: str,
    ) -> None:
        self._embedding_service = embedding_service
        self._vector_db_client = vector_db_client
        self._top_k = top_k
        self._similarity_threshold = similarity_threshold
        self._collection_name = collection_name

    async def retrieve_chunks(self, query: str) -> list[RetrievedChunk]:
        """
        Recupera os chunks mais relevantes para a query fornecida.

        O pipeline executa:
        1. Gera o embedding da query via EmbeddingService.
        2. Busca no Qdrant os top-K chunks acima do limiar de similaridade.
        3. Mapeia os resultados para RetrievedChunk com content, score e metadata.

        Args:
            query: Texto da pergunta do usuário.

        Returns:
            Lista de RetrievedChunk ordenada por score decrescente (ordem do Qdrant).
            Retorna lista vazia se nenhum resultado superar o limiar de similaridade.

        Raises:
            RuntimeError: Se a conexão com o Qdrant falhar.
        """
        # 1. Gerar embedding da query
        query_vector = await self._embedding_service.embed(query)

        # 2. Buscar no Qdrant
        try:
            results = await self._vector_db_client.search(
                collection_name=self._collection_name,
                query_vector=query_vector,
                limit=self._top_k,
                score_threshold=self._similarity_threshold,
            )
        except Exception as exc:
            raise RuntimeError(
                f"Falha ao conectar ao banco vetorial Qdrant "
                f"(coleção '{self._collection_name}'): {exc}"
            ) from exc

        # 3. Mapear resultados para RetrievedChunk
        chunks: list[RetrievedChunk] = []
        for hit in results:
            payload = hit.payload or {}
            metadata = SourceReference(
                filename=payload.get("filename", ""),
                page=payload.get("page"),
                position=payload.get("position"),
            )
            chunk = RetrievedChunk(
                content=payload.get("content", ""),
                score=hit.score,
                metadata=metadata,
            )
            chunks.append(chunk)

        # Resultados já vêm ordenados por score decrescente do Qdrant
        return chunks
