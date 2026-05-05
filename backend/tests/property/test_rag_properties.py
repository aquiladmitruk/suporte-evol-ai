"""
Testes de propriedade para RAGService.

Propriedades verificadas:
- P8: Seleção de exatamente N chunks relevantes (Requisito 5.2)
- P9: Fallback quando similaridade abaixo do limiar (Requisito 5.4)
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from app.rag_service import RAGService


# ---------------------------------------------------------------------------
# Estratégias Hypothesis
# ---------------------------------------------------------------------------


_hit_counter = 0


def _scored_point_strategy(min_score: float = 0.0, max_score: float = 1.0):
    """Gera um mock de ScoredPoint do Qdrant com score e payload aleatórios."""
    return st.builds(
        lambda score, filename, page, position, uid: _make_hit(
            score=score,
            payload={
                "content": f"chunk content uid={uid}",
                "filename": filename,
                "page": page,
                "position": position,
            },
        ),
        score=st.floats(
            min_value=min_score,
            max_value=max_score,
            allow_nan=False,
            allow_infinity=False,
        ),
        filename=st.text(
            alphabet=st.characters(
                whitelist_categories=("Lu", "Ll", "Nd"),
                whitelist_characters="._-",
            ),
            min_size=1,
            max_size=50,
        ),
        page=st.one_of(st.none(), st.integers(min_value=1, max_value=9999)),
        position=st.one_of(st.none(), st.integers(min_value=0, max_value=9999)),
        uid=st.integers(min_value=0, max_value=10_000_000),
    )


def _make_hit(score: float, payload: dict) -> MagicMock:
    """Cria um mock de ScoredPoint do Qdrant."""
    hit = MagicMock()
    hit.score = score
    hit.payload = payload
    return hit


def _make_rag_service(
    hits: list,
    top_k: int,
    similarity_threshold: float,
    collection_name: str = "evol_docs",
) -> RAGService:
    """Cria um RAGService com mocks de EmbeddingService e AsyncQdrantClient."""
    embedding_service = MagicMock()
    embedding_service.embed = AsyncMock(return_value=[0.1, 0.2, 0.3])

    vector_db_client = MagicMock()
    # O Qdrant já filtra por score_threshold e limita por top_k;
    # simulamos esse comportamento no mock
    filtered = [h for h in hits if h.score >= similarity_threshold]
    filtered_sorted = sorted(filtered, key=lambda h: h.score, reverse=True)
    limited = filtered_sorted[:top_k]
    vector_db_client.search = AsyncMock(return_value=limited)

    return RAGService(
        embedding_service=embedding_service,
        vector_db_client=vector_db_client,
        top_k=top_k,
        similarity_threshold=similarity_threshold,
        collection_name=collection_name,
    )


# ---------------------------------------------------------------------------
# Propriedade 8: Seleção de exatamente N chunks relevantes
# ---------------------------------------------------------------------------

# Feature: evol-erp-ai-assistant, Property 8: Seleção de exatamente N chunks relevantes
# Valida: Requisito 5.2


@given(
    hits=st.lists(
        _scored_point_strategy(min_score=0.0, max_score=1.0),
        max_size=20,
        unique_by=lambda h: h.payload["content"],
    ),
    top_k=st.integers(min_value=1, max_value=10),
    similarity_threshold=st.floats(
        min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False
    ),
)
@settings(max_examples=100)
@pytest.mark.asyncio
async def test_property_rag_selects_min_m_n_chunks(
    hits: list, top_k: int, similarity_threshold: float
):
    """
    **Validates: Requirements 5.2**

    Propriedade 8: Para qualquer resultado de busca semântica com M chunks disponíveis
    acima do limiar de similaridade, o RAGService deve selecionar min(M, N) chunks,
    onde N é o valor configurado em RAG_TOP_K, sem duplicatas e ordenados por score
    decrescente.
    """
    rag = _make_rag_service(
        hits=hits,
        top_k=top_k,
        similarity_threshold=similarity_threshold,
    )

    result = await rag.retrieve_chunks("query de teste")

    # Calcular M: número de chunks acima do limiar
    m = sum(1 for h in hits if h.score >= similarity_threshold)
    expected_count = min(m, top_k)

    # O resultado deve conter exatamente min(M, N) chunks
    assert len(result) == expected_count, (
        f"Esperado {expected_count} chunks (min({m}, {top_k})), "
        f"mas obteve {len(result)}"
    )

    # Não deve haver duplicatas (verificar por conteúdo, que é único via uid)
    seen = set()
    for chunk in result:
        assert chunk.content not in seen, f"Chunk duplicado encontrado: {chunk.content}"
        seen.add(chunk.content)

    # Deve estar ordenado por score decrescente
    scores = [chunk.score for chunk in result]
    assert scores == sorted(scores, reverse=True), (
        f"Chunks não estão ordenados por score decrescente: {scores}"
    )


# ---------------------------------------------------------------------------
# Propriedade 9: Fallback quando similaridade abaixo do limiar
# ---------------------------------------------------------------------------

# Feature: evol-erp-ai-assistant, Property 9: Fallback quando similaridade abaixo do limiar
# Valida: Requisito 5.4


@given(
    scores=st.lists(
        st.floats(min_value=0.0, max_value=0.9999, allow_nan=False, allow_infinity=False),
        min_size=0,
        max_size=15,
    ),
    similarity_threshold=st.floats(
        min_value=0.0001,
        max_value=1.0,
        allow_nan=False,
        allow_infinity=False,
    ),
)
@settings(max_examples=100)
@pytest.mark.asyncio
async def test_property_rag_returns_empty_when_all_below_threshold(
    scores: list[float], similarity_threshold: float
):
    """
    **Validates: Requirements 5.4**

    Propriedade 9: Para qualquer consulta cuja busca semântica retorne apenas chunks
    com score abaixo do limiar configurado (RAG_SIMILARITY_THRESHOLD), o RAGService
    deve retornar uma lista vazia de chunks.
    """
    # Garantir que todos os scores estão abaixo do limiar
    below_threshold_scores = [s for s in scores if s < similarity_threshold]

    hits = [
        _make_hit(
            score=score,
            payload={
                "content": f"chunk {i}",
                "filename": "doc.pdf",
                "page": i,
                "position": i,
            },
        )
        for i, score in enumerate(below_threshold_scores)
    ]

    rag = _make_rag_service(
        hits=hits,
        top_k=10,
        similarity_threshold=similarity_threshold,
    )

    result = await rag.retrieve_chunks("query sem resultados relevantes")

    assert result == [], (
        f"Esperado lista vazia quando todos os scores {below_threshold_scores} "
        f"estão abaixo do limiar {similarity_threshold}, mas obteve {len(result)} chunks"
    )
