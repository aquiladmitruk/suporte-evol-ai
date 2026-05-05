"""
Router de chat para o Assistente de IA do ERP Evol.

Expõe o endpoint POST /api/chat que processa mensagens do usuário
via ChatService e retorna a resposta gerada pelo LLM.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException

from app.chat_service import ChatService
from app.dependencies import get_chat_service
from app.models import ChatRequest, ChatResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    """
    Processa uma mensagem do usuário e retorna a resposta do assistente.

    Args:
        request: Payload validado pelo Pydantic com session_id, message e history.
        chat_service: Instância do ChatService injetada via dependência FastAPI.

    Returns:
        ChatResponse com a resposta gerada e as referências de fontes.

    Raises:
        HTTPException 503: Se o serviço de busca semântica (Qdrant) estiver indisponível.
        HTTPException 502: Se o serviço de geração de resposta (LLM) estiver indisponível.
    """
    try:
        return await chat_service.process_message(
            session_id=request.session_id,
            user_message=request.message,
            client_history=request.history,
        )
    except RuntimeError as exc:
        error_message = str(exc)
        logger.exception("Erro ao processar mensagem de chat: %s", error_message)

        # Distinguir erros do Qdrant (503) dos erros do LLM (502)
        if "qdrant" in error_message.lower() or "banco vetorial" in error_message.lower():
            raise HTTPException(
                status_code=503,
                detail="Serviço de busca semântica indisponível. Tente novamente em instantes.",
            ) from exc
        else:
            raise HTTPException(
                status_code=502,
                detail="Serviço de geração de resposta indisponível. Tente novamente em instantes.",
            ) from exc
