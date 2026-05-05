# Plano de Implementação — Frontend do Assistente de IA do ERP Evol

## Tarefas

- [x] 1. Scaffolding e configuração do projeto
  - [x] 1.1 Inicializar projeto Vite + React + TypeScript
  - [x] 1.2 Instalar e configurar Tailwind CSS com `darkMode: 'class'`
  - [x] 1.3 Instalar dependências: `react-markdown`, `remark-gfm`, `uuid`
  - [x] 1.4 Configurar fonte Inter via Google Fonts no `index.html`
  - [x] 1.5 Criar `.env.example` com `VITE_API_URL=http://localhost:8000`
  - [x] 1.6 Configurar animação `fade-in` no `tailwind.config.js`

- [x] 2. Tipos TypeScript e camada de serviço
  - [x] 2.1 Criar `src/types.ts` com `ChatMessage`, `ChatRequest`, `ChatResponse`, `SourceReference` e `UIMessage`
  - [x] 2.2 Criar `src/services/api.ts` com a função `sendChatMessage`
  - [x] 2.3 Tratar erros HTTP (não-2xx) e erros de rede em `api.ts`

- [x] 3. Hook `useTheme`
  - [x] 3.1 Criar `src/hooks/useTheme.ts`
  - [x] 3.2 Implementar leitura de preferência do `localStorage` com fallback para `prefers-color-scheme`
  - [x] 3.3 Implementar efeito que aplica/remove classe `dark` no `document.documentElement`
  - [x] 3.4 Implementar persistência da preferência no `localStorage` ao alternar

- [x] 4. Hook `useChat`
  - [x] 4.1 Criar `src/hooks/useChat.ts`
  - [x] 4.2 Implementar geração e persistência do `session_id` no `sessionStorage`
  - [x] 4.3 Implementar estado `messages` e `isLoading`
  - [x] 4.4 Implementar função `sendMessage` com validação de mensagem vazia
  - [x] 4.5 Implementar adição de mensagem do usuário ao histórico antes da requisição
  - [x] 4.6 Implementar chamada à API e adição da resposta do assistente ao histórico
  - [x] 4.7 Implementar tratamento de erro com adição de mensagem de erro ao histórico

- [x] 5. Componente `TypingIndicator`
  - [x] 5.1 Criar `src/components/TypingIndicator.tsx`
  - [x] 5.2 Implementar animação de três pontos com `animate-bounce` e delays escalonados
  - [x] 5.3 Adicionar `role="status"` e `aria-label="Assistente digitando..."`

- [x] 6. Componente `SourceList`
  - [x] 6.1 Criar `src/components/SourceList.tsx`
  - [x] 6.2 Renderizar lista de fontes com `filename` e `page` (quando presente)
  - [x] 6.3 Ocultar componente quando `sources` estiver vazio ou ausente

- [x] 7. Componente `MessageBubble`
  - [x] 7.1 Criar `src/components/MessageBubble.tsx`
  - [x] 7.2 Implementar estilo diferenciado para mensagens do usuário (direita, indigo)
  - [x] 7.3 Implementar renderização Markdown via `react-markdown` + `remark-gfm` para mensagens do assistente
  - [x] 7.4 Implementar estilo de mensagem de erro (`isError = true`)
  - [x] 7.5 Integrar `SourceList` abaixo das mensagens do assistente
  - [x] 7.6 Adicionar animação `animate-fade-in` na entrada da bolha

- [x] 8. Componente `ChatWindow`
  - [x] 8.1 Criar `src/components/ChatWindow.tsx`
  - [x] 8.2 Renderizar lista de `MessageBubble` a partir do array `messages`
  - [x] 8.3 Implementar scroll automático para a última mensagem com `useRef` + `useEffect`
  - [x] 8.4 Exibir `TypingIndicator` quando `isLoading = true`

- [x] 9. Componente `ChatInput`
  - [x] 9.1 Criar `src/components/ChatInput.tsx`
  - [x] 9.2 Implementar `<textarea>` com envio por `Enter` (sem `Shift`) e nova linha por `Shift+Enter`
  - [x] 9.3 Implementar botão de envio com ícone SVG de seta
  - [x] 9.4 Desabilitar textarea e botão quando `isLoading = true`
  - [x] 9.5 Limpar campo após envio
  - [x] 9.6 Adicionar `aria-label` no textarea e no botão

- [x] 10. Componente `Header`
  - [x] 10.1 Criar `src/components/Header.tsx`
  - [x] 10.2 Exibir nome/logo "Assistente ERP Evol"
  - [x] 10.3 Implementar botão de toggle de tema com ícone de sol/lua
  - [x] 10.4 Adicionar `aria-label` descritivo no botão de tema

- [x] 11. Composição em `App.tsx` e `main.tsx`
  - [x] 11.1 Compor `Header`, `ChatWindow` e `ChatInput` em `App.tsx`
  - [x] 11.2 Conectar hooks `useTheme` e `useChat` ao `App.tsx`
  - [x] 11.3 Configurar layout `flex-col h-screen` com área de mensagens expansível

- [x] 12. Estilos globais e configuração final
  - [x] 12.1 Configurar diretivas Tailwind em `src/index.css`
  - [x] 12.2 Adicionar estilos para elementos Markdown (tabelas, código, blockquotes) em `index.css`
  - [x] 12.3 Garantir que o scroll da `ChatWindow` não vaze para o body

- [x] 13. README e documentação
  - [x] 13.1 Criar `README.md` com instruções de instalação, configuração de `.env` e execução
  - [x] 13.2 Documentar os scripts disponíveis (`dev`, `build`, `preview`)
