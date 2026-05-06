"""
Modelos de dados Pydantic para o Assistente de IA do ERP Evol.

Todos os modelos usam Pydantic v2.
"""

from typing import Literal, Optional

from pydantic import BaseModel, field_validator


class ChatMessage(BaseModel):
    """Representa uma mensagem individual no histórico de conversa."""

    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    """Payload de requisição ao endpoint POST /api/chat."""

    session_id: str
    message: str
    history: list[ChatMessage] = []

    @field_validator("session_id")
    @classmethod
    def session_id_not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("session_id não pode ser vazio ou conter apenas espaços")
        return v

    @field_validator("message")
    @classmethod
    def message_not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("message não pode ser vazio ou conter apenas espaços")
        return v


class SourceReference(BaseModel):
    """Referência à fonte de um trecho recuperado da base de conhecimento."""

    filename: str
    page: Optional[int] = None
    position: Optional[int] = None


class ChatResponse(BaseModel):
    """Payload de resposta do endpoint POST /api/chat."""

    response: str
    sources: list[SourceReference] = []


class RetrievedChunk(BaseModel):
    """Chunk recuperado do banco vetorial com score de similaridade."""

    content: str
    score: float
    metadata: SourceReference


