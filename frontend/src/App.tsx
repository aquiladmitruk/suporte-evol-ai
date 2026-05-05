import { useState } from 'react';
import Header from './components/Header';
import ChatWindow from './components/ChatWindow';
import ChatInput from './components/ChatInput';
import Sidebar from './components/Sidebar';
import { useTheme } from './hooks/useTheme';
import { useChat } from './hooks/useChat';

export default function App() {
  const { theme, toggleTheme } = useTheme();
  const { messages, isLoading, sendMessage } = useChat();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex flex-col h-screen bg-[#f3f4f6] dark:bg-gray-950 transition-colors overflow-hidden">

      {/* Barra superior — ocupa toda a largura */}
      <Header
        theme={theme}
        onToggleTheme={toggleTheme}
        sidebarOpen={sidebarOpen}
        onToggleSidebar={() => setSidebarOpen((prev) => !prev)}
      />

      {/* Linha do meio: sidebar + área de chat */}
      <div className="flex flex-1 overflow-hidden">
        <Sidebar isOpen={sidebarOpen} />

        {/* Coluna principal: apenas o histórico de mensagens */}
        <main className="flex flex-col flex-1 overflow-hidden bg-white dark:bg-gray-950">
          <ChatWindow messages={messages} isLoading={isLoading} onSuggestionClick={sendMessage} />
        </main>
      </div>

      {/* Barra inferior — ocupa toda a largura, acima da sidebar */}
      <div className="bg-[#e5e7eb] dark:bg-gray-900 py-3">
        <div className="max-w-3xl mx-auto px-4">
          <ChatInput onSend={sendMessage} isLoading={isLoading} />
        </div>
      </div>

    </div>
  );
}
