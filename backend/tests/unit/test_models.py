"""
Testes unitários para os modelos Pydantic em app/models.py.

Cobre os requisitos 7.1 e 7.3:
- ChatRequest aceita payloads válidos
- ChatRequest rejeita session_id e message vazios ou somente espaços
"""

import pytest
from pydantic import ValidationError

from app.models import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    RetrievedChunk,
    SourceReference,
)


# ---------------------------------------------------------------------------
# ChatMessage
# ---------------------------------------------------------------------------


class TestChatMessage:
    def test_valid_user_message(self):
        msg = ChatMessage(role="user", content="Olá")
        assert msg.role == "user"
        assert msg.content == "Olá"

    def test_valid_assistant_message(self):
        msg = ChatMessage(role="assistant", content="Como posso ajudar?")
        assert msg.role == "assistant"

    def test_invalid_role_raises(self):
        with pytest.raises(ValidationError):
            ChatMessage(role="system", content="texto")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# ChatRequest — campos obrigatórios e validações
# ---------------------------------------------------------------------------


class TestChatRequest:
    def test_valid_request(self):
        req = ChatRequest(session_id="abc-123", message="Como emito NF?")
        assert req.session_id == "abc-123"
        assert req.message == "Como emito NF?"
        assert req.history == []

    def test_valid_request_with_history(self):
        history = [
            ChatMessage(role="user", content="Olá"),
            ChatMessage(role="assistant", content="Olá! Como posso ajudar?"),
        ]
        req = ChatRequest(session_id="s1", message="Pergunta", history=history)
        assert len(req.history) == 2

    # session_id validation
    def test_empty_session_id_raises(self):
        with pytest.raises(ValidationError):
            ChatRequest(session_id="", message="Pergunta")

    def test_blank_session_id_raises(self):
        with pytest.raises(ValidationError):
            ChatRequest(session_id="   ", message="Pergunta")

    def test_tab_only_session_id_raises(self):
        with pytest.raises(ValidationError):
            ChatRequest(session_id="\t\n", message="Pergunta")

    # message validation
    def test_empty_message_raises(self):
        with pytest.raises(ValidationError):
            ChatRequest(session_id="s1", message="")

    def test_blank_message_raises(self):
        with pytest.raises(ValidationError):
            ChatRequest(session_id="s1", message="   ")

    def test_tab_only_message_raises(self):
        with pytest.raises(ValidationError):
            ChatRequest(session_id="s1", message="\t\n")

    def test_missing_session_id_raises(self):
        with pytest.raises(ValidationError):
            ChatRequest(message="Pergunta")  # type: ignore[call-arg]

    def test_missing_message_raises(self):
        with pytest.raises(ValidationError):
            ChatRequest(session_id="s1")  # type: ignore[call-arg]


# ---------------------------------------------------------------------------
# SourceReference
# ---------------------------------------------------------------------------


class TestSourceReference:
    def test_minimal(self):
        src = SourceReference(filename="manual.pdf")
        assert src.filename == "manual.pdf"
        assert src.page is None
        assert src.position is None

    def test_full(self):
        src = SourceReference(filename="manual.pdf", page=10, position=3)
        assert src.page == 10
        assert src.position == 3


# ---------------------------------------------------------------------------
# ChatResponse
# ---------------------------------------------------------------------------


class TestChatResponse:
    def test_minimal(self):
        resp = ChatResponse(response="Resposta do assistente")
        assert resp.response == "Resposta do assistente"
        assert resp.sources == []

    def test_with_sources(self):
        sources = [SourceReference(filename="doc.pdf", page=1)]
        resp = ChatResponse(response="Texto", sources=sources)
        assert len(resp.sources) == 1


# ---------------------------------------------------------------------------
# RetrievedChunk
# ---------------------------------------------------------------------------


class TestRetrievedChunk:
    def test_valid(self):
        chunk = RetrievedChunk(
            content="Trecho relevante",
            score=0.92,
            metadata=SourceReference(filename="doc.txt"),
        )
        assert chunk.score == 0.92


