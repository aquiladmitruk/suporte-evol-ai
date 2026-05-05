"""
Testes unitários para RAGService.

Verifica comportamentos específicos do serviço de busca semântica:
- Lista vazia quando nenhum chunk supera o limiar de similaridade
- Ordenação por score decrescente
- Mapeamento correto dos campos do payload Qdrant para RetrievedChunk
- Propagação de erros de conexão como RuntimeError
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.rag_service import RAGService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_hit(score: float, payload: dict) -> MagicMock:
    """Cria um mock de ScoredPoint do Qdrant."""
    hit = MagicMock()
    hit.score = score
    hit.payload = payload
    return hit


def _make_rag_service(
    hits: list,
    top_k: int = 5,
    similarity_threshold: float = 0.7,
    collection_name: str = "evol_docs",
) -> RAGService:
    """Cria um RAGService com mocks de EmbeddingService e AsyncQdrantClient."""
    embedding_service = MagicMock()
    embedding_service.embed = AsyncMock(return_value=[0.1, 0.2, 0.3])

    vector_db_client = MagicMock()
    vector_db_client.search = AsyncMock(return_value=hits)

    return RAGService(
        embedding_service=embedding_service,
        vector_db_client=vector_db_client,
        top_k=top_k,
        similarity_threshold=similarity_threshold,
        collection_name=collection_name,
    )


# ---------------------------------------------------------------------------
# Testes: lista vazia
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_retrieve_chunks_returns_empty_when_no_results():
    """Retorna lista vazia quando o Qdrant não retorna nenhum resultado."""
    rag = _make_rag_service(hits=[])
    result = await rag.retrieve_chunks("alguma query")
    assert result == []


@pytest.mark.asyncio
async def test_retrieve_chunks_returns_empty_when_qdrant_returns_empty_list():
    """Retorna lista vazia quando o Qdrant retorna lista vazia (nenhum chunk acima do limiar)."""
    # O Qdrant já filtra por score_threshold; se retornar vazio, RAGService também retorna vazio
    rag = _make_rag_service(hits=[])
    result = await rag.retrieve_chunks("query sem resultados")
    assert result == []


# ---------------------------------------------------------------------------
# Testes: mapeamento de campos
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_retrieve_chunks_maps_payload_fields_correctly():
    """Mapeia corretamente content, score, filename, page e position do payload."""
    payload = {
        "content": "Texto do chunk",
        "filename": "manual.pdf",
        "page": 10,
        "position": 3,
    }
    hits = [_make_hit(score=0.95, payload=payload)]
    rag = _make_rag_service(hits=hits)

    result = await rag.retrieve_chunks("query")

    assert len(result) == 1
    chunk = result[0]
    assert chunk.content == "Texto do chunk"
    assert chunk.score == 0.95
    assert chunk.metadata.filename == "manual.pdf"
    assert chunk.metadata.page == 10
    assert chunk.metadata.position == 3


@pytest.mark.asyncio
async def test_retrieve_chunks_handles_missing_optional_fields():
    """Lida com payload sem campos opcionais (page e position ausentes)."""
    payload = {
        "content": "Conteúdo sem página",
        "filename": "doc.txt",
    }
    hits = [_make_hit(score=0.80, payload=payload)]
    rag = _make_rag_service(hits=hits)

    result = await rag.retrieve_chunks("query")

    assert len(result) == 1
    chunk = result[0]
    assert chunk.metadata.page is None
    assert chunk.metadata.position is None


@pytest.mark.asyncio
async def test_retrieve_chunks_handles_empty_payload():
    """Lida com payload vazio sem lançar exceção."""
    hits = [_make_hit(score=0.75, payload={})]
    rag = _make_rag_service(hits=hits)

    result = await rag.retrieve_chunks("query")

    assert len(result) == 1
    assert result[0].content == ""
    assert result[0].metadata.filename == ""


# ---------------------------------------------------------------------------
# Testes: ordenação por score decrescente
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_retrieve_chunks_preserves_qdrant_order():
    """Preserva a ordem retornada pelo Qdrant (score decrescente)."""
    hits = [
        _make_hit(score=0.95, payload={"content": "A", "filename": "a.pdf"}),
        _make_hit(score=0.85, payload={"content": "B", "filename": "b.pdf"}),
        _make_hit(score=0.75, payload={"content": "C", "filename": "c.pdf"}),
    ]
    rag = _make_rag_service(hits=hits)

    result = await rag.retrieve_chunks("query")

    assert len(result) == 3
    assert result[0].score == 0.95
    assert result[1].score == 0.85
    assert result[2].score == 0.75


# ---------------------------------------------------------------------------
# Testes: parâmetros passados ao Qdrant
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_retrieve_chunks_passes_correct_params_to_qdrant():
    """Passa collection_name, query_vector, limit e score_threshold corretos ao Qdrant."""
    embedding_service = MagicMock()
    embedding_service.embed = AsyncMock(return_value=[0.5, 0.6])

    vector_db_client = MagicMock()
    vector_db_client.search = AsyncMock(return_value=[])

    rag = RAGService(
        embedding_service=embedding_service,
        vector_db_client=vector_db_client,
        top_k=3,
        similarity_threshold=0.8,
        collection_name="minha_colecao",
    )

    await rag.retrieve_chunks("minha query")

    vector_db_client.search.assert_called_once_with(
        collection_name="minha_colecao",
        query_vector=[0.5, 0.6],
        limit=3,
        score_threshold=0.8,
    )


@pytest.mark.asyncio
async def test_retrieve_chunks_calls_embed_with_query():
    """Chama EmbeddingService.embed com o texto exato da query."""
    embedding_service = MagicMock()
    embedding_service.embed = AsyncMock(return_value=[0.1])

    vector_db_client = MagicMock()
    vector_db_client.search = AsyncMock(return_value=[])

    rag = RAGService(
        embedding_service=embedding_service,
        vector_db_client=vector_db_client,
        top_k=5,
        similarity_threshold=0.7,
        collection_name="evol_docs",
    )

    await rag.retrieve_chunks("Como emitir nota fiscal?")

    embedding_service.embed.assert_called_once_with("Como emitir nota fiscal?")


# ---------------------------------------------------------------------------
# Testes: tratamento de erros de conexão
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_retrieve_chunks_raises_runtime_error_on_connection_failure():
    """Propaga falha de conexão com Qdrant como RuntimeError com mensagem descritiva."""
    embedding_service = MagicMock()
    embedding_service.embed = AsyncMock(return_value=[0.1, 0.2])

    vector_db_client = MagicMock()
    vector_db_client.search = AsyncMock(
        side_effect=ConnectionError("Connection refused")
    )

    rag = RAGService(
        embedding_service=embedding_service,
        vector_db_client=vector_db_client,
        top_k=5,
        similarity_threshold=0.7,
        collection_name="evol_docs",
    )

    with pytest.raises(RuntimeError) as exc_info:
        await rag.retrieve_chunks("query")

    assert "Qdrant" in str(exc_info.value)
    assert "evol_docs" in str(exc_info.value)


@pytest.mark.asyncio
async def test_retrieve_chunks_runtime_error_wraps_original_exception():
    """O RuntimeError encadeia a exceção original como causa."""
    original_error = OSError("Network unreachable")

    embedding_service = MagicMock()
    embedding_service.embed = AsyncMock(return_value=[0.1])

    vector_db_client = MagicMock()
    vector_db_client.search = AsyncMock(side_effect=original_error)

    rag = RAGService(
        embedding_service=embedding_service,
        vector_db_client=vector_db_client,
        top_k=5,
        similarity_threshold=0.7,
        collection_name="evol_docs",
    )

    with pytest.raises(RuntimeError) as exc_info:
        await rag.retrieve_chunks("query")

    assert exc_info.value.__cause__ is original_error
