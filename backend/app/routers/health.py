"""
Router de health check para o Assistente de IA do ERP Evol.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/health")
async def health_check() -> JSONResponse:
    """
    Verifica se o serviço está em execução.

    Returns:
        JSON com status "ok" e HTTP 200.
    """
    return JSONResponse(content={"status": "ok"}, status_code=200)
