"""
Serviço de geração de embeddings para o Assistente de IA do ERP Evol.

Usa o cliente AsyncOpenAI para gerar embeddings de texto via API
(modelo text-embedding-3-small, 1536 dimensões).
"""

import logging

import openai

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Gera embeddings de texto usando a API OpenAI.

    Args:
        model: Identificador do modelo de embeddings (ex.: "text-embedding-3-small").
        api_key: Chave de API do provedor de embeddings.
    """

    def __init__(self, model: str, api_key: str) -> None:
        self._model = model
        self._client = openai.AsyncOpenAI(api_key=api_key)

    async def embed(self, text: str) -> list[float]:
        """
        Gera o embedding de um único texto.

        Args:
            text: Texto a ser convertido em embedding.

        Returns:
            Lista de floats representando o vetor de embedding.

        Raises:
            RuntimeError: Se a chamada à API falhar.
        """
        try:
            response = await self._client.embeddings.create(
                model=self._model,
                input=text,
            )
        except Exception as exc:
            raise RuntimeError(
                f"Falha ao gerar embedding com o modelo '{self._model}': {exc}"
            ) from exc

        return response.data[0].embedding
