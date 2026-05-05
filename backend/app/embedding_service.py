"""
Serviço de geração de embeddings para o Assistente de IA do ERP Evol.

Usa o cliente AsyncOpenAI para gerar embeddings de texto via API.
"""

import logging

import openai

logger = logging.getLogger(__name__)

# Preços por 1 000 tokens (USD)
_EMBEDDING_PRICING: dict[str, float] = {
    "text-embedding-3-small": 0.00002,
    "text-embedding-3-large": 0.00013,
    "text-embedding-ada-002":  0.00010,
}

_USD_TO_BRL = 5.75


def _estimate_embedding_cost(model: str, tokens: int) -> float:
    price = _EMBEDDING_PRICING.get(model, 0.0)
    return (tokens / 1_000) * price


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
        # Acumulador de tokens consumidos nesta instância
        self.total_tokens_used: int = 0

    async def embed(self, text: str) -> list[float]:
        """
        Gera o embedding de um único texto.

        Args:
            text: Texto a ser convertido em embedding.

        Returns:
            Lista de floats representando o vetor de embedding.
        """
        response = await self._client.embeddings.create(
            model=self._model,
            input=text,
        )
        if response.usage:
            tokens = response.usage.total_tokens
            self.total_tokens_used += tokens
            cost_usd = _estimate_embedding_cost(self._model, tokens)
            cost_brl = cost_usd * _USD_TO_BRL
            logger.info(
                "Embedding [%s] | tokens=%d | U$ %.6f | R$ %.6f",
                self._model,
                tokens,
                cost_usd,
                cost_brl,
            )
        return response.data[0].embedding

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Gera embeddings para uma lista de textos em uma única chamada à API.

        Args:
            texts: Lista de textos a serem convertidos em embeddings.

        Returns:
            Lista de vetores de embedding na mesma ordem dos textos de entrada.
            Retorna lista vazia se ``texts`` for vazio.
        """
        if not texts:
            return []

        response = await self._client.embeddings.create(
            model=self._model,
            input=texts,
        )
        if response.usage:
            tokens = response.usage.total_tokens
            self.total_tokens_used += tokens
            cost_usd = _estimate_embedding_cost(self._model, tokens)
            cost_brl = cost_usd * _USD_TO_BRL
            logger.info(
                "Embedding batch [%s] | textos=%d | tokens=%d | U$ %.6f | R$ %.6f",
                self._model,
                len(texts),
                tokens,
                cost_usd,
                cost_brl,
            )
        # A API retorna os embeddings ordenados pelo índice original
        sorted_data = sorted(response.data, key=lambda item: item.index)
        return [item.embedding for item in sorted_data]
