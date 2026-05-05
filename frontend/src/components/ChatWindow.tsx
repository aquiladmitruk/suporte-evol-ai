import { useRef, useEffect } from 'react';
import MessageBubble from './MessageBubble';
import TypingIndicator from './TypingIndicator';
import { UIMessage } from '../types';

interface ChatWindowProps {
  messages: UIMessage[];
  isLoading: boolean;
  onSuggestionClick: (message: string) => void;
}

const SUGGESTIONS = [
  'Como faço para emitir uma nota fiscal no ERP Evol?',
  'Quais relatórios financeiros estão disponíveis no sistema?',
];

export default function ChatWindow({ messages, isLoading, onSuggestionClick }: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  if (messages.length === 0 && !isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center px-4">

        {/* Sugestões de perguntas — lado a lado, acima do ícone */}
        <div className="flex flex-row gap-3 w-full max-w-xl mb-8">
          {SUGGESTIONS.map((suggestion) => (
            <button
              key={suggestion}
              onClick={() => onSuggestionClick(suggestion)}
              className="flex-1 text-left px-4 py-3 rounded-xl border border-gray-200 dark:border-gray-700
                bg-gray-100 dark:bg-gray-800
                text-sm text-gray-700 dark:text-gray-300
                hover:border-indigo-400 dark:hover:border-indigo-500
                hover:bg-gray-200 dark:hover:bg-indigo-900/20
                hover:text-indigo-700 dark:hover:text-indigo-300
                transition-colors"
            >
              {suggestion}
            </button>
          ))}
        </div>

        <div className="w-12 h-12 rounded-full bg-indigo-100 dark:bg-indigo-900 flex items-center justify-center mb-4">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="text-indigo-600 dark:text-indigo-400"
            aria-hidden="true"
          >
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
        </div>
        <h2 className="text-base font-semibold text-gray-800 dark:text-gray-200 mb-1">
          Assistente ERP Evol
        </h2>
        <p className="text-sm text-gray-500 dark:text-gray-400 max-w-sm">
          Olá! Como posso ajudar você com o ERP Evol hoje?
        </p>
      </div>
    );
  }

  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-3xl mx-auto py-4 pb-2">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        {isLoading && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
