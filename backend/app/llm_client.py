"""
Cliente LLM para o Assistente de IA do ERP Evol.

Wrapper sobre o cliente OpenAI assíncrono para chamadas ao modelo de linguagem.
"""

import logging

import openai

logger = logging.getLogger(__name__)

# Preços por 1 000 tokens (USD) — modelos OpenAI mais comuns
_LLM_PRICING: dict[str, dict[str, float]] = {
    "gpt-4.1":        {"input": 0.002000, "output": 0.008000},
    "gpt-4.1-mini":   {"input": 0.000400, "output": 0.001600},
    "gpt-4.1-nano":   {"input": 0.000100, "output": 0.000400},
    "gpt-4o":         {"input": 0.005000, "output": 0.015000},
    "gpt-4o-mini":    {"input": 0.000150, "output": 0.000600},
    "gpt-4-turbo":    {"input": 0.010000, "output": 0.030000},
    "gpt-3.5-turbo":  {"input": 0.000500, "output": 0.001500},
}

_USD_TO_BRL = 5.75


def _estimate_llm_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    """Estima o custo em USD para uma chamada ao LLM."""
    # Tenta match exato, depois prefixo
    pricing = _LLM_PRICING.get(model)
    if not pricing:
        for key, val in _LLM_PRICING.items():
            if model.startswith(key):
                pricing = val
                break
    if not pricing:
        return 0.0
    return (prompt_tokens / 1_000) * pricing["input"] + (completion_tokens / 1_000) * pricing["output"]


class LLMClient:
    """
    Cliente assíncrono para chamadas ao LLM via API OpenAI.

    Args:
        model: Identificador do modelo LLM (ex.: 'gpt-4o').
        api_key: Chave de API do provedor LLM.
    """

    def __init__(self, model: str, api_key: str) -> None:
        self._model = model
        self._client = openai.AsyncOpenAI(api_key=api_key)

    async def complete(self, messages: list[dict]) -> str:
        """
        Envia a lista de mensagens ao LLM e retorna o texto da resposta.

        Loga o consumo de tokens e custo estimado em USD e BRL após cada chamada.

        Args:
            messages: Lista de mensagens no formato OpenAI
                      [{"role": "system"|"user"|"assistant", "content": "..."}].

        Returns:
            Texto da resposta gerada pelo LLM (choices[0].message.content).

        Raises:
            RuntimeError: Se a chamada à API falhar (timeout, autenticação, etc.).
        """
        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=messages,  # type: ignore[arg-type]
            )

            # Log de consumo de tokens
            if response.usage:
                prompt_tokens = response.usage.prompt_tokens
                completion_tokens = response.usage.completion_tokens
                total_tokens = response.usage.total_tokens
                cost_usd = _estimate_llm_cost(self._model, prompt_tokens, completion_tokens)
                cost_brl = cost_usd * _USD_TO_BRL
                logger.info(
                    "LLM [%s] | prompt=%d  completion=%d  total=%d tokens"
                    " | U$ %.6f | R$ %.6f",
                    self._model,
                    prompt_tokens,
                    completion_tokens,
                    total_tokens,
                    cost_usd,
                    cost_brl,
                )

            return response.choices[0].message.content or ""
        except openai.AuthenticationError as exc:
            raise RuntimeError(
                f"Falha de autenticação na API do LLM: {exc}"
            ) from exc
        except openai.RateLimitError as exc:
            raise RuntimeError(
                f"Limite de requisições atingido na API do LLM: {exc}"
            ) from exc
        except openai.APITimeoutError as exc:
            raise RuntimeError(
                f"Timeout na chamada à API do LLM: {exc}"
            ) from exc
        except openai.APIConnectionError as exc:
            raise RuntimeError(
                f"Falha de conexão com a API do LLM: {exc}"
            ) from exc
        except openai.APIError as exc:
            raise RuntimeError(
                f"Erro na API do LLM: {exc}"
            ) from exc
