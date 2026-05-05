"""
Dependências FastAPI para o Assistente de IA do ERP Evol.

Funções de dependência que instanciam os serviços como singletons,
usando o padrão de injeção de dependência do FastAPI.
"""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from qdrant_client import AsyncQdrantClient

from app.chat_service import ChatService
from app.config import Settings, settings
from app.embedding_service import EmbeddingService
from app.llm_client import LLMClient
from app.prompt_builder import PromptBuilder
from app.rag_service import RAGService
from app.session_store import SessionStore


def get_settings() -> Settings:
    """Retorna o singleton de configurações da aplicação."""
    return settings  # type: ignore[return-value]


@lru_cache(maxsize=1)
def _create_embedding_service() -> EmbeddingService:
    """Cria o singleton de EmbeddingService."""
    s = get_settings()
    return EmbeddingService(model=s.EMBEDDING_MODEL, api_key=s.LLM_API_KEY)


def get_embedding_service() -> EmbeddingService:
    """Retorna o singleton de EmbeddingService."""
    return _create_embedding_service()


@lru_cache(maxsize=1)
def _create_qdrant_client() -> AsyncQdrantClient:
    """Cria o singleton de AsyncQdrantClient."""
    s = get_settings()
    return AsyncQdrantClient(url=s.QDRANT_URL, api_key=s.QDRANT_API_KEY)


def get_qdrant_client() -> AsyncQdrantClient:
    """Retorna o singleton de AsyncQdrantClient."""
    return _create_qdrant_client()


@lru_cache(maxsize=1)
def _create_rag_service() -> RAGService:
    """Cria o singleton de RAGService."""
    s = get_settings()
    return RAGService(
        embedding_service=_create_embedding_service(),
        vector_db_client=_create_qdrant_client(),
        top_k=s.RAG_TOP_K,
        similarity_threshold=s.RAG_SIMILARITY_THRESHOLD,
        collection_name=s.QDRANT_COLLECTION,
    )


def get_rag_service() -> RAGService:
    """Retorna o singleton de RAGService."""
    return _create_rag_service()


@lru_cache(maxsize=1)
def _create_session_store() -> SessionStore:
    """Cria o singleton de SessionStore."""
    s = get_settings()
    return SessionStore(ttl_seconds=s.SESSION_TTL_SECONDS)


def get_session_store() -> SessionStore:
    """Retorna o singleton de SessionStore."""
    return _create_session_store()


@lru_cache(maxsize=1)
def _create_prompt_builder() -> PromptBuilder:
    """Cria o singleton de PromptBuilder."""
    return PromptBuilder()


def get_prompt_builder() -> PromptBuilder:
    """Retorna o singleton de PromptBuilder."""
    return _create_prompt_builder()


@lru_cache(maxsize=1)
def _create_llm_client() -> LLMClient:
    """Cria o singleton de LLMClient."""
    s = get_settings()
    return LLMClient(model=s.LLM_MODEL, api_key=s.LLM_API_KEY)


def get_llm_client() -> LLMClient:
    """Retorna o singleton de LLMClient."""
    return _create_llm_client()


@lru_cache(maxsize=1)
def _create_chat_service() -> ChatService:
    """Cria o singleton de ChatService compondo todos os serviços."""
    return ChatService(
        rag_service=_create_rag_service(),
        session_store=_create_session_store(),
        prompt_builder=_create_prompt_builder(),
        llm_client=_create_llm_client(),
    )


def get_chat_service(
    _rag: Annotated[RAGService, Depends(get_rag_service)] = None,  # type: ignore[assignment]
    _session: Annotated[SessionStore, Depends(get_session_store)] = None,  # type: ignore[assignment]
    _prompt: Annotated[PromptBuilder, Depends(get_prompt_builder)] = None,  # type: ignore[assignment]
    _llm: Annotated[LLMClient, Depends(get_llm_client)] = None,  # type: ignore[assignment]
) -> ChatService:
    """Retorna o singleton de ChatService."""
    return _create_chat_service()
