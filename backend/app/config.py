"""
Configuração centralizada do Assistente de IA para Suporte do ERP Evol.

Lê todas as variáveis de ambiente via pydantic-settings.
Variáveis obrigatórias ausentes encerram o processo com sys.exit(1).

Uso:
    from app.config import settings
    print(settings.QDRANT_URL)
"""

import logging
import os
import sys
from typing import Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

# Variáveis de ambiente obrigatórias (usadas no teste de propriedade P17)
REQUIRED_VARS: list[str] = [
    "QDRANT_URL",
    "LLM_API_KEY",
    "LLM_MODEL",
    "EMBEDDING_MODEL",
    "CORS_ALLOWED_ORIGINS",
]


class Settings(BaseSettings):
    """
    Configurações da aplicação lidas exclusivamente de variáveis de ambiente.

    Variáveis obrigatórias:
        QDRANT_URL, LLM_API_KEY, LLM_MODEL, EMBEDDING_MODEL, CORS_ALLOWED_ORIGINS

    Variáveis opcionais (com defaults):
        QDRANT_API_KEY, QDRANT_COLLECTION, RAG_TOP_K, RAG_SIMILARITY_THRESHOLD,
        SESSION_TTL_SECONDS, CHUNK_SIZE, CHUNK_OVERLAP
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # Variáveis obrigatórias
    # ------------------------------------------------------------------

    QDRANT_URL: str
    LLM_API_KEY: str
    LLM_MODEL: str
    EMBEDDING_MODEL: str
    CORS_ALLOWED_ORIGINS: str  # Comma-separated list of origins

    # ------------------------------------------------------------------
    # Variáveis opcionais (com defaults)
    # ------------------------------------------------------------------

    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION: str = "evol_docs"
    RAG_TOP_K: int = 5
    RAG_SIMILARITY_THRESHOLD: float = 0.7
    SESSION_TTL_SECONDS: int = 3600
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 64

    # ------------------------------------------------------------------
    # Propriedades derivadas
    # ------------------------------------------------------------------

    @property
    def cors_origins_list(self) -> list[str]:
        """Retorna a lista de origens CORS como lista de strings."""
        return [
            origin.strip()
            for origin in self.CORS_ALLOWED_ORIGINS.split(",")
            if origin.strip()
        ]

    # ------------------------------------------------------------------
    # Validadores
    # ------------------------------------------------------------------

    @field_validator("RAG_TOP_K")
    @classmethod
    def validate_top_k(cls, v: int) -> int:
        if v < 1:
            raise ValueError("RAG_TOP_K deve ser maior ou igual a 1")
        return v

    @field_validator("RAG_SIMILARITY_THRESHOLD")
    @classmethod
    def validate_similarity_threshold(cls, v: float) -> float:
        if not (0.0 <= v <= 1.0):
            raise ValueError("RAG_SIMILARITY_THRESHOLD deve estar entre 0.0 e 1.0")
        return v

    @field_validator("SESSION_TTL_SECONDS")
    @classmethod
    def validate_ttl(cls, v: int) -> int:
        if v < 1:
            raise ValueError("SESSION_TTL_SECONDS deve ser maior ou igual a 1")
        return v

    @field_validator("CHUNK_SIZE")
    @classmethod
    def validate_chunk_size(cls, v: int) -> int:
        if v < 1:
            raise ValueError("CHUNK_SIZE deve ser maior ou igual a 1")
        return v

    @field_validator("CHUNK_OVERLAP")
    @classmethod
    def validate_chunk_overlap(cls, v: int) -> int:
        if v < 0:
            raise ValueError("CHUNK_OVERLAP deve ser maior ou igual a 0")
        return v


def _check_required_vars() -> list[str]:
    """Retorna a lista de variáveis obrigatórias ausentes no ambiente atual."""
    return [var for var in REQUIRED_VARS if not os.environ.get(var)]


def _load_settings() -> Settings:
    """
    Carrega as configurações e encerra o processo se variáveis obrigatórias
    estiverem ausentes, registrando quais variáveis estão faltando.
    """
    missing = _check_required_vars()

    if missing:
        logger.error(
            "Inicialização abortada. As seguintes variáveis de ambiente obrigatórias "
            "estão ausentes: %s",
            ", ".join(missing),
        )
        sys.exit(1)

    try:
        return Settings()
    except Exception as exc:  # noqa: BLE001
        logger.error("Erro ao carregar configurações: %s", exc)
        sys.exit(1)


class _LazySettings:
    """
    Proxy lazy para o singleton de Settings.

    O objeto Settings real é instanciado apenas na primeira vez que um
    atributo é acessado, não na importação do módulo. Isso permite que
    testes importem REQUIRED_VARS sem disparar sys.exit(1).
    """

    _instance: Optional[Settings] = None

    def _get_instance(self) -> Settings:
        if self._instance is None:
            self._instance = _load_settings()
        return self._instance

    def __getattr__(self, name: str):  # type: ignore[override]
        return getattr(self._get_instance(), name)

    def __repr__(self) -> str:
        return repr(self._get_instance())


# Singleton — a instância real é criada na primeira vez que um atributo é acessado
settings: Settings = _LazySettings()  # type: ignore[assignment]
