"""
Construtor de prompts para o Assistente de IA do ERP Evol.

Responsável por montar o system prompt com restrições de escopo e o contexto
de documentação recuperado pelo pipeline RAG, além de formatar o histórico
de mensagens no formato esperado pelo LLM.
"""

from app.models import ChatMessage, RetrievedChunk

SCOPE_RESTRICTION_INSTRUCTION = (
    "Você é um assistente consultivo do ERP Evol. "
    "Sua função é EXCLUSIVAMENTE orientar e educar os usuários sobre como usar o sistema. "
    "Você NÃO deve executar ações, inserir dados, alterar configurações ou simular a "
    "execução de qualquer operação no ERP Evol. "
    "Quando o usuário solicitar que você execute uma ação no ERP Evol, informe que sua "
    "função é exclusivamente orientativa e indique o caminho no sistema para que o "
    "usuário realize a ação por conta própria."
)

NO_CONTEXT_INSTRUCTION = (
    "Não foram encontradas informações relevantes na base de conhecimento do ERP Evol "
    "para a consulta do usuário. Informe ao usuário que não foi possível encontrar "
    "informações específicas sobre o tema consultado na documentação disponível e "
    "sugira que ele entre em contato com o suporte do ERP Evol para obter ajuda."
)


class PromptBuilder:
    """Constrói prompts para o LLM com restrições de escopo e contexto RAG."""

    def build_system_prompt(self, retrieved_chunks: list[RetrievedChunk]) -> str:
        """
        Constrói o system prompt com a instrução de restrição de escopo e o
        contexto de documentação recuperado pelo pipeline RAG.

        Args:
            retrieved_chunks: Lista de chunks recuperados do banco vetorial.
                Se vazia, inclui instrução de fallback informando ausência de contexto.

        Returns:
            String com o system prompt completo.
        """
        parts = [SCOPE_RESTRICTION_INSTRUCTION]

        if retrieved_chunks:
            total = len(retrieved_chunks)
            context_parts = []
            for i, chunk in enumerate(retrieved_chunks, start=1):
                source = chunk.metadata
                header = f"--- Trecho {i} de {total} (fonte: {source.filename}"
                if source.page is not None:
                    header += f", página: {source.page}"
                header += ") ---"
                context_parts.append(f"{header}\n{chunk.content}")

            context_block = "\n\n".join(context_parts)
            parts.append(
                "Use os trechos de documentação abaixo como base para sua resposta. "
                "Responda com base nas informações fornecidas na documentação.\n\n"
                + context_block
            )
        else:
            parts.append(NO_CONTEXT_INSTRUCTION)

        return "\n\n".join(parts)

    def build_messages(
        self,
        system_prompt: str,
        history: list[ChatMessage],
        user_message: str,
    ) -> list[dict]:
        """
        Monta a lista de mensagens no formato OpenAI para envio ao LLM.

        Args:
            system_prompt: Texto do system prompt já construído.
            history: Histórico de mensagens da sessão.
            user_message: Mensagem atual do usuário.

        Returns:
            Lista de dicts no formato [{"role": ..., "content": ...}].
        """
        messages: list[dict] = [{"role": "system", "content": system_prompt}]

        for msg in history:
            messages.append({"role": msg.role, "content": msg.content})

        messages.append({"role": "user", "content": user_message})

        return messages
