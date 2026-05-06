"""
Testes unitários para ChatService.

Verifica o comportamento do orquestrador de chat em diferentes cenários:
- RAG retorna lista vazia
- LLM lança RuntimeError
- Fluxo normal com atualização do histórico
- ChatResponse contém as fontes dos chunks recuperados
"""

import pytest

from app.chat_service import ChatService
from app.models import ChatMessage, ChatResponse, RetrievedChunk, SourceReference
from app.prompt_builder import PromptBuilder
from app.session_store import SessionStore


# ---------------------------------------------------------------------------
# Stubs / Fakes
# ---------------------------------------------------------------------------


class FakeRAGService:
    """RAGService fake que retorna uma lista configurável de chunks."""

    def __init__(self, chunks: list[RetrievedChunk]) -> None:
        self._chunks = chunks
        self.last_query: str | None = None

    async def retrieve_chunks(self, query: str, source_file: str | None = None) -> list[RetrievedChunk]:
        self.last_query = query
        return self._chunks


class FakeRAGServiceError:
    """RAGService fake que sempre lança RuntimeError."""

    async def retrieve_chunks(self, query: str, source_file: str | None = None) -> list[RetrievedChunk]:
        raise RuntimeError("Falha ao conectar ao banco vetorial Qdrant")


class FakeLLMClient:
    """LLMClient fake que retorna uma resposta configurável."""

    def __init__(self, response: str = "Resposta do assistente") -> None:
        self._response = response
        self.last_messages: list[dict] | None = None

    async def complete(self, messages: list[dict]) -> str:
        self.last_messages = messages
        return self._response


class FakeLLMClientError:
    """LLMClient fake que sempre lança RuntimeError."""

    async def complete(self, messages: list[dict]) -> str:
        raise RuntimeError("Erro na API do LLM")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def make_chunk(filename: str = "manual.pdf", page: int = 1) -> RetrievedChunk:
    return RetrievedChunk(
        content="Conteúdo do chunk",
        score=0.9,
        metadata=SourceReference(filename=filename, page=page),
    )


def make_service(
    chunks: list[RetrievedChunk] | None = None,
    llm_response: str = "Resposta do assistente",
    session_store: SessionStore | None = None,
) -> tuple[ChatService, FakeRAGService, FakeLLMClient, SessionStore]:
    rag = FakeRAGService(chunks or [])
    llm = FakeLLMClient(llm_response)
    store = session_store or SessionStore()
    prompt_builder = PromptBuilder()
    service = ChatService(
        rag_service=rag,
        session_store=store,
        prompt_builder=prompt_builder,
        llm_client=llm,
    )
    return service, rag, llm, store


# ---------------------------------------------------------------------------
# Testes
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_empty_rag_calls_build_system_prompt_with_empty_list():
    """Quando RAG retorna lista vazia, build_system_prompt é chamado com []."""
    service, rag, llm, store = make_service(chunks=[])

    response = await service.process_message(
        session_id="session-1",
        user_message="Como emito uma NF?",
        client_history=[],
    )

    # RAG foi consultado com a mensagem do usuário
    assert rag.last_query == "Como emito uma NF?"

    # A resposta deve ser retornada normalmente
    assert isinstance(response, ChatResponse)
    assert response.response == "Resposta do assistente"

    # Sem chunks, sources deve ser lista vazia
    assert response.sources == []

    # O system prompt enviado ao LLM deve conter a instrução de fallback
    assert llm.last_messages is not None
    system_content = llm.last_messages[0]["content"]
    assert "não foram encontradas informações relevantes" in system_content.lower()


@pytest.mark.asyncio
async def test_llm_runtime_error_propagates_without_modifying_history():
    """Quando LLM lança RuntimeError, a exceção é propagada e o histórico não é modificado."""
    store = SessionStore()
    rag = FakeRAGService([])
    llm = FakeLLMClientError()
    prompt_builder = PromptBuilder()
    service = ChatService(
        rag_service=rag,
        session_store=store,
        prompt_builder=prompt_builder,
        llm_client=llm,
    )

    with pytest.raises(RuntimeError, match="Erro na API do LLM"):
        await service.process_message(
            session_id="session-err",
            user_message="Pergunta qualquer",
            client_history=[],
        )

    # Histórico não deve ter sido modificado
    history = store.get_history("session-err")
    assert history == []


@pytest.mark.asyncio
async def test_qdrant_runtime_error_propagates_without_modifying_history():
    """Quando RAGService lança RuntimeError (Qdrant 503), a exceção é propagada sem modificar o histórico."""
    store = SessionStore()
    rag = FakeRAGServiceError()
    llm = FakeLLMClient()
    prompt_builder = PromptBuilder()
    service = ChatService(
        rag_service=rag,
        session_store=store,
        prompt_builder=prompt_builder,
        llm_client=llm,
    )

    with pytest.raises(RuntimeError, match="Qdrant"):
        await service.process_message(
            session_id="session-qdrant-err",
            user_message="Pergunta qualquer",
            client_history=[],
        )

    # Histórico não deve ter sido modificado
    history = store.get_history("session-qdrant-err")
    assert history == []


@pytest.mark.asyncio
async def test_normal_flow_updates_history():
    """No fluxo normal, o histórico é atualizado com a mensagem do usuário e a resposta."""
    service, rag, llm, store = make_service(
        chunks=[make_chunk()],
        llm_response="Aqui está a orientação sobre NF.",
    )

    await service.process_message(
        session_id="session-normal",
        user_message="Como emito uma NF?",
        client_history=[],
    )

    history = store.get_history("session-normal")
    assert len(history) == 2
    assert history[0].role == "user"
    assert history[0].content == "Como emito uma NF?"
    assert history[1].role == "assistant"
    assert history[1].content == "Aqui está a orientação sobre NF."


@pytest.mark.asyncio
async def test_chat_response_contains_chunk_sources():
    """ChatResponse deve conter as fontes (metadata) dos chunks recuperados."""
    chunk1 = make_chunk(filename="manual_nfe.pdf", page=42)
    chunk2 = make_chunk(filename="guia_rapido.pdf", page=7)
    service, _, _, _ = make_service(chunks=[chunk1, chunk2])

    response = await service.process_message(
        session_id="session-sources",
        user_message="Como emito uma NF?",
        client_history=[],
    )

    assert len(response.sources) == 2
    assert response.sources[0].filename == "manual_nfe.pdf"
    assert response.sources[0].page == 42
    assert response.sources[1].filename == "guia_rapido.pdf"
    assert response.sources[1].page == 7


@pytest.mark.asyncio
async def test_uses_server_history_when_available():
    """Quando o servidor tem histórico, ele é usado em vez do client_history."""
    store = SessionStore()
    # Pré-popular o histórico do servidor
    store.append_message("session-hist", ChatMessage(role="user", content="Olá"))
    store.append_message(
        "session-hist", ChatMessage(role="assistant", content="Olá! Como posso ajudar?")
    )

    service, _, llm, _ = make_service(session_store=store)

    client_history = [
        ChatMessage(role="user", content="Mensagem do cliente que não deve ser usada")
    ]

    await service.process_message(
        session_id="session-hist",
        user_message="Nova pergunta",
        client_history=client_history,
    )

    # O histórico enviado ao LLM deve conter as mensagens do servidor, não do cliente
    assert llm.last_messages is not None
    # messages[0] é o system prompt, messages[1] e [2] são o histórico do servidor
    roles_and_contents = [
        (m["role"], m["content"]) for m in llm.last_messages[1:]
    ]
    assert ("user", "Olá") in roles_and_contents
    assert ("assistant", "Olá! Como posso ajudar?") in roles_and_contents
    # A mensagem do cliente não deve aparecer
    assert ("user", "Mensagem do cliente que não deve ser usada") not in roles_and_contents


@pytest.mark.asyncio
async def test_uses_client_history_when_server_history_empty():
    """Quando o servidor não tem histórico, o client_history é usado."""
    service, _, llm, _ = make_service()

    client_history = [
        ChatMessage(role="user", content="Pergunta anterior"),
        ChatMessage(role="assistant", content="Resposta anterior"),
    ]

    await service.process_message(
        session_id="session-new",
        user_message="Nova pergunta",
        client_history=client_history,
    )

    assert llm.last_messages is not None
    roles_and_contents = [
        (m["role"], m["content"]) for m in llm.last_messages[1:]
    ]
    assert ("user", "Pergunta anterior") in roles_and_contents
    assert ("assistant", "Resposta anterior") in roles_and_contents
