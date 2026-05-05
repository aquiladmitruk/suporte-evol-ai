"""
Aplicação FastAPI principal do Assistente de IA do ERP Evol.

Configura CORS, registra os routers e define o lifespan da aplicação.
"""

import logging
import logging.config
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import chat, documents, health

# ---------------------------------------------------------------------------
# Configuração de logging
# Propaga os loggers da aplicação para o handler do uvicorn, garantindo que
# mensagens INFO (incluindo custo de tokens) apareçam no console do servidor.
# ---------------------------------------------------------------------------
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(levelname)s:\t  %(name)s - %(message)s",
        },
    },
    "handlers": {
        "default": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        # Loggers da aplicação — nível INFO para exibir custo de tokens
        "app": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        },
        "scripts": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False,
        },
        # Silencia loggers muito verbosos de libs externas
        "httpx": {"level": "WARNING", "propagate": True},
        "openai": {"level": "WARNING", "propagate": True},
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Gerencia o ciclo de vida da aplicação FastAPI."""
    logger.info("Assistente de IA - ERP Evol está pronto para receber requisições.")
    yield
    logger.info("Assistente de IA - ERP Evol encerrando.")


def create_app() -> FastAPI:
    """Cria e configura a aplicação FastAPI."""
    app = FastAPI(
        title="Assistente de IA - ERP Evol",
        description="API do Assistente de IA para Suporte do ERP Evol",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Registrar routers com prefixo /api
    app.include_router(health.router, prefix="/api")
    app.include_router(chat.router, prefix="/api")
    app.include_router(documents.router, prefix="/api")

    return app


app = create_app()
