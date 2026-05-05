"""
Testes unitários para os endpoints da API FastAPI.

Testa os endpoints GET /api/health e POST /api/chat usando TestClient
com mocks para o ChatService (sem chamar serviços reais).
"""

import os
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

# Configurar variáveis de ambiente antes de importar a aplicação
os.environ.setdefault("QDRANT_URL", "http://localhost:6333")
os.environ.setdefault("LLM_API_KEY", "test-api-key")
os.environ.setdefault("LLM_MODEL", "gpt-4o")
os.environ.setdefault("EMBEDDING_MODEL", "text-embedding-3-small")
os.environ.setdefault("CORS_ALLOWED_ORIGINS", "http://localhost:3000")


@pytest.fixture
def mock_chat_service() -> MagicMock:
    """Cria um mock do ChatService para uso nos testes."""
    from app.models import ChatResponse, SourceReference

    service = MagicMock()
    service.process_message = AsyncMock(
        return_value=ChatResponse(
            response="Resposta de teste do assistente.",
            sources=[SourceReference(filename="manual.pdf", page=1)],
        )
    )
    return service


@pytest.fixture
def client(mock_chat_service: MagicMock) -> TestClient:
    """Cria um TestClient com o ChatService substituído pelo mock."""
    from app.dependencies import get_chat_service
    from app.main import app

    app.dependency_overrides[get_chat_service] = lambda: mock_chat_service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


class TestHealthEndpoint:
    """Testes para o endpoint GET /api/health."""

    def test_health_returns_200(self, client: TestClient) -> None:
        """GET /api/health deve retornar HTTP 200."""
        response = client.get("/api/health")
        assert response.status_code == 200

    def test_health_returns_ok_status(self, client: TestClient) -> None:
        """GET /api/health deve retornar JSON com status 'ok'."""
        response = client.get("/api/health")
        assert response.json() == {"status": "ok"}


class TestChatEndpoint:
    """Testes para o endpoint POST /api/chat."""

    def test_chat_with_valid_payload_returns_200(
        self, client: TestClient, mock_chat_service: MagicMock
    ) -> None:
        """POST /api/chat com payload válido deve retornar HTTP 200."""
        payload = {
            "session_id": "test-session-123",
            "message": "Como emito uma nota fiscal?",
            "history": [],
        }
        response = client.post("/api/chat", json=payload)
        assert response.status_code == 200

    def test_chat_with_valid_payload_returns_response_field(
        self, client: TestClient
    ) -> None:
        """POST /api/chat com payload válido deve retornar JSON com campo 'response'."""
        payload = {
            "session_id": "test-session-123",
            "message": "Como emito uma nota fiscal?",
            "history": [],
        }
        response = client.post("/api/chat", json=payload)
        data = response.json()
        assert "response" in data
        assert data["response"] == "Resposta de teste do assistente."

    def test_chat_with_missing_payload_returns_422(self, client: TestClient) -> None:
        """POST /api/chat sem payload deve retornar HTTP 422."""
        response = client.post("/api/chat")
        assert response.status_code == 422

    def test_chat_with_empty_body_returns_422(self, client: TestClient) -> None:
        """POST /api/chat com body vazio deve retornar HTTP 422."""
        response = client.post("/api/chat", json={})
        assert response.status_code == 422

    def test_chat_with_empty_message_returns_422(self, client: TestClient) -> None:
        """POST /api/chat com message vazio deve retornar HTTP 422."""
        payload = {
            "session_id": "test-session-123",
            "message": "",
            "history": [],
        }
        response = client.post("/api/chat", json=payload)
        assert response.status_code == 422

    def test_chat_with_whitespace_message_returns_422(self, client: TestClient) -> None:
        """POST /api/chat com message contendo apenas espaços deve retornar HTTP 422."""
        payload = {
            "session_id": "test-session-123",
            "message": "   ",
            "history": [],
        }
        response = client.post("/api/chat", json=payload)
        assert response.status_code == 422

    def test_chat_with_missing_session_id_returns_422(self, client: TestClient) -> None:
        """POST /api/chat sem session_id deve retornar HTTP 422."""
        payload = {
            "message": "Como emito uma nota fiscal?",
            "history": [],
        }
        response = client.post("/api/chat", json=payload)
        assert response.status_code == 422

    def test_chat_with_missing_message_returns_422(self, client: TestClient) -> None:
        """POST /api/chat sem message deve retornar HTTP 422."""
        payload = {
            "session_id": "test-session-123",
            "history": [],
        }
        response = client.post("/api/chat", json=payload)
        assert response.status_code == 422

    def test_chat_qdrant_error_returns_503(
        self, client: TestClient, mock_chat_service: MagicMock
    ) -> None:
        """POST /api/chat com erro do Qdrant deve retornar HTTP 503."""
        mock_chat_service.process_message = AsyncMock(
            side_effect=RuntimeError(
                "Falha ao conectar ao banco vetorial Qdrant (coleção 'evol_docs'): connection refused"
            )
        )
        payload = {
            "session_id": "test-session-123",
            "message": "Como emito uma nota fiscal?",
            "history": [],
        }
        response = client.post("/api/chat", json=payload)
        assert response.status_code == 503
        assert "busca semântica" in response.json()["detail"]

    def test_chat_llm_error_returns_502(
        self, client: TestClient, mock_chat_service: MagicMock
    ) -> None:
        """POST /api/chat com erro do LLM deve retornar HTTP 502."""
        mock_chat_service.process_message = AsyncMock(
            side_effect=RuntimeError("Falha de autenticação na API do LLM: invalid key")
        )
        payload = {
            "session_id": "test-session-123",
            "message": "Como emito uma nota fiscal?",
            "history": [],
        }
        response = client.post("/api/chat", json=payload)
        assert response.status_code == 502
        assert "geração de resposta" in response.json()["detail"]

    def test_chat_calls_service_with_correct_args(
        self, client: TestClient, mock_chat_service: MagicMock
    ) -> None:
        """POST /api/chat deve chamar ChatService.process_message com os argumentos corretos."""
        payload = {
            "session_id": "my-session-id",
            "message": "Qual o prazo para emissão de NF?",
            "history": [
                {"role": "user", "content": "Olá"},
                {"role": "assistant", "content": "Olá! Como posso ajudar?"},
            ],
        }
        client.post("/api/chat", json=payload)

        mock_chat_service.process_message.assert_called_once()
        call_kwargs = mock_chat_service.process_message.call_args.kwargs
        assert call_kwargs["session_id"] == "my-session-id"
        assert call_kwargs["user_message"] == "Qual o prazo para emissão de NF?"
        assert len(call_kwargs["client_history"]) == 2
