import { useState } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { sendChatMessage } from '../services/api';
import type { UIMessage, ChatMessage } from '../types';

// Gerar session_id na inicialização — sessionStorage é limpo ao recarregar a página,
// então sempre geramos um novo UUID (não tentamos recuperar do sessionStorage).
const sessionId = uuidv4();
sessionStorage.setItem('session_id', sessionId);

export function useChat(): {
  messages: UIMessage[];
  isLoading: boolean;
  sendMessage: (content: string) => Promise<void>;
} {
  const [messages, setMessages] = useState<UIMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  async function sendMessage(content: string): Promise<void> {
    // 4.4 — Validação: ignorar mensagens vazias
    if (content.trim() === '') {
      return;
    }

    // 4.5 — Adicionar mensagem do usuário ao histórico antes da requisição
    const userMessage: UIMessage = {
      id: uuidv4(),
      role: 'user',
      content,
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // 4.6 — Construir histórico a partir das mensagens atuais (excluindo erros)
      // Usamos o callback do setMessages para garantir acesso ao estado mais recente,
      // mas como precisamos do histórico antes de atualizar, capturamos via closure.
      // O histórico inclui a mensagem do usuário recém-adicionada.
      const history: ChatMessage[] = [...messages, userMessage]
        .filter((msg) => !msg.isError)
        .map(({ role, content: msgContent }) => ({ role, content: msgContent }));

      const data = await sendChatMessage({
        session_id: sessionId,
        message: content,
        history,
      });

      const assistantMessage: UIMessage = {
        id: uuidv4(),
        role: 'assistant',
        content: data.response,
        sources: data.sources,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch {
      // 4.7 — Tratamento de erro: adicionar mensagem de erro ao histórico
      const errorMessage: UIMessage = {
        id: uuidv4(),
        role: 'assistant',
        content: 'Não foi possível obter uma resposta. Verifique sua conexão e tente novamente.',
        isError: true,
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      // 4.9 — Sempre desativar loading ao final
      setIsLoading(false);
    }
  }

  return { messages, isLoading, sendMessage };
}
