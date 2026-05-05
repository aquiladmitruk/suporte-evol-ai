# Documento de Design — Frontend do Assistente de IA do ERP Evol

## Visão Geral

O frontend é uma Single Page Application (SPA) em React 18+ com TypeScript, construída com Vite e estilizada com Tailwind CSS. A aplicação oferece uma interface de chat profissional e responsiva para o Assistente de IA do ERP Evol, comunicando-se com a API FastAPI via `fetch` nativo.

A direção estética adotada é **Modern Corporate Minimalist**: paleta neutra com acentos azul-índigo, tipografia limpa, hierarquia visual clara e micro-animações sutis que reforçam o feedback sem distrair o usuário.

---

## Arquitetura

### Estrutura de Pastas

```
frontend/
├── public/
│   └── favicon.svg
├── src/
│   ├── components/
│   │   ├── ChatInput.tsx        # Campo de entrada + botão de envio
│   │   ├── ChatWindow.tsx       # Área de mensagens com scroll
│   │   ├── Header.tsx           # Cabeçalho com logo e toggle de tema
│   │   ├── MessageBubble.tsx    # Bolha de mensagem (user/assistant)
│   │   ├── SourceList.tsx       # Lista de fontes abaixo da resposta
│   │   └── TypingIndicator.tsx  # Animação de carregamento
│   ├── hooks/
│   │   ├── useChat.ts           # Lógica principal de chat e estado
│   │   └── useTheme.ts          # Lógica de tema claro/escuro
│   ├── services/
│   │   └── api.ts               # Comunicação com a API FastAPI
│   ├── types.ts                 # Tipos TypeScript compartilhados
│   ├── App.tsx                  # Componente raiz
│   ├── main.tsx                 # Entry point
│   └── index.css                # Estilos globais + diretivas Tailwind
├── index.html
├── tailwind.config.js
├── postcss.config.js
├── tsconfig.json
├── tsconfig.node.json
├── vite.config.ts
├── .env.example
└── README.md
```

---

## Tipos TypeScript (`src/types.ts`)

```ts
export type ChatMessage = {
  role: 'user' | 'assistant';
  content: string;
};

export type ChatRequest = {
  session_id: string;
  message: string;
  history: ChatMessage[];
};

export type ChatResponse = {
  response: string;
  sources: SourceReference[];
};

export type SourceReference = {
  filename: string;
  page?: number;
};

// Tipo interno para mensagens com metadados de UI
export type UIMessage = ChatMessage & {
  id: string;
  sources?: SourceReference[];
  isError?: boolean;
};
```

---

## Camada de Serviço (`src/services/api.ts`)

Responsável por toda comunicação HTTP com o backend.

```ts
const API_BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`Erro na API: ${response.status}`);
  }

  return response.json() as Promise<ChatResponse>;
}
```

- Erros HTTP (não-2xx) lançam `Error` com status
- Erros de rede (sem conexão, timeout) propagam o erro nativo do `fetch`
- Sem retry automático — o usuário decide quando tentar novamente

---

## Hooks

### `useTheme` (`src/hooks/useTheme.ts`)

Gerencia o tema claro/escuro da aplicação.

**Estado:** `theme: 'light' | 'dark'`

**Inicialização:**
1. Lê `localStorage.getItem('theme')`
2. Se não encontrado, usa `window.matchMedia('(prefers-color-scheme: dark)').matches`

**Efeito:** Ao mudar o tema, aplica/remove a classe `dark` no `document.documentElement` e persiste no `localStorage`.

**Interface:**
```ts
function useTheme(): {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
}
```

---

### `useChat` (`src/hooks/useChat.ts`)

Gerencia todo o estado e lógica do chat.

**Estado:**
- `messages: UIMessage[]` — lista de mensagens exibidas
- `isLoading: boolean` — controla o indicador de carregamento
- `sessionId: string` — UUID v4 gerado/recuperado do `sessionStorage`

**Inicialização do `sessionId`:**
```ts
const sessionId = sessionStorage.getItem('session_id') ?? (() => {
  const id = uuidv4();
  sessionStorage.setItem('session_id', id);
  return id;
})();
```

**Função `sendMessage(content: string)`:**
1. Valida que `content.trim()` não está vazio
2. Adiciona mensagem do usuário ao estado
3. Define `isLoading = true`
4. Chama `sendChatMessage` com `session_id`, `message` e `history` (mensagens anteriores sem `isError`)
5. Em caso de sucesso: adiciona resposta do assistente com `sources`
6. Em caso de erro: adiciona mensagem de erro com `isError = true`
7. Define `isLoading = false`

**Interface:**
```ts
function useChat(): {
  messages: UIMessage[];
  isLoading: boolean;
  sendMessage: (content: string) => Promise<void>;
}
```

---

## Componentes

### `Header` (`src/components/Header.tsx`)

Cabeçalho fixo no topo da página.

- Exibe o logotipo/nome "Assistente ERP Evol"
- Botão de toggle de tema com ícone de sol/lua
- `aria-label` descritivo no botão
- Estilo: fundo sólido com borda inferior sutil, `z-index` elevado

**Props:**
```ts
interface HeaderProps {
  theme: 'light' | 'dark';
  onToggleTheme: () => void;
}
```

---

### `ChatWindow` (`src/components/ChatWindow.tsx`)

Área de mensagens com scroll automático.

- Renderiza a lista de `UIMessage` via `MessageBubble`
- Exibe `TypingIndicator` quando `isLoading = true`
- Usa `useRef` + `useEffect` para scroll automático ao final
- Padding generoso para não sobrepor o `ChatInput`

**Props:**
```ts
interface ChatWindowProps {
  messages: UIMessage[];
  isLoading: boolean;
}
```

---

### `MessageBubble` (`src/components/MessageBubble.tsx`)

Bolha individual de mensagem.

**Mensagem do usuário:**
- Alinhada à direita
- Fundo azul-índigo (`bg-indigo-600`)
- Texto branco
- Bordas arredondadas com canto inferior direito reto

**Mensagem do assistente:**
- Alinhada à esquerda
- Fundo cinza claro / cinza escuro no dark mode
- Texto renderizado via `react-markdown` + `remark-gfm`
- Exibe `SourceList` abaixo quando há fontes

**Mensagem de erro:**
- Alinhada à esquerda
- Fundo vermelho suave com ícone de alerta
- Texto em vermelho escuro

**Props:**
```ts
interface MessageBubbleProps {
  message: UIMessage;
}
```

---

### `SourceList` (`src/components/SourceList.tsx`)

Lista de fontes documentais abaixo da resposta do assistente.

- Exibida apenas quando `sources.length > 0`
- Cada item mostra `filename` e, se presente, `página X`
- Estilo discreto: texto menor, cor secundária, ícone de documento

**Props:**
```ts
interface SourceListProps {
  sources: SourceReference[];
}
```

---

### `TypingIndicator` (`src/components/TypingIndicator.tsx`)

Indicador animado de que o assistente está processando.

- Três pontos pulsantes com animação CSS (`animate-bounce` com delays escalonados)
- `role="status"` e `aria-label="Assistente digitando..."` para acessibilidade
- Mesmo estilo visual da bolha do assistente

---

### `ChatInput` (`src/components/ChatInput.tsx`)

Campo de entrada fixo na parte inferior da tela.

- `<textarea>` com auto-resize (1 linha por padrão, expande com o conteúdo)
- `Enter` sem `Shift` envia; `Shift+Enter` insere nova linha
- Botão de envio com ícone de seta
- Desabilitado quando `isLoading = true`
- Placeholder: "Digite sua pergunta sobre o ERP Evol..."
- `aria-label` no textarea e no botão

**Props:**
```ts
interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading: boolean;
}
```

---

## Composição em `App.tsx`

```tsx
export default function App() {
  const { theme, toggleTheme } = useTheme();
  const { messages, isLoading, sendMessage } = useChat();

  return (
    <div className="flex flex-col h-screen bg-gray-50 dark:bg-gray-950">
      <Header theme={theme} onToggleTheme={toggleTheme} />
      <main className="flex-1 overflow-hidden">
        <ChatWindow messages={messages} isLoading={isLoading} />
      </main>
      <ChatInput onSend={sendMessage} isLoading={isLoading} />
    </div>
  );
}
```

---

## Design Visual

### Paleta de Cores

| Token | Light | Dark | Uso |
|---|---|---|---|
| Background principal | `gray-50` | `gray-950` | Fundo da página |
| Background header | `white` | `gray-900` | Cabeçalho |
| Bolha usuário | `indigo-600` | `indigo-500` | Mensagens do usuário |
| Bolha assistente | `white` | `gray-800` | Mensagens do assistente |
| Borda | `gray-200` | `gray-700` | Separadores |
| Acento/ação | `indigo-600` | `indigo-400` | Botões, links |
| Erro | `red-50` / `red-700` | `red-900` / `red-300` | Mensagens de erro |
| Texto principal | `gray-900` | `gray-50` | Corpo do texto |
| Texto secundário | `gray-500` | `gray-400` | Fontes, metadados |

### Tipografia

- Fonte: `Inter` (Google Fonts) — sans-serif profissional e legível
- Tamanho base: `text-sm` (14px) para mensagens, `text-base` para input
- Código inline: `font-mono` com fundo `gray-100` / `gray-800`

### Animações

- Entrada de mensagem: `animate-fade-in` (opacity 0→1, translateY 4px→0, 200ms)
- Typing indicator: `animate-bounce` com delays de 0ms, 150ms, 300ms
- Toggle de tema: transição suave `transition-colors duration-200`

---

## Configuração do Tailwind (`tailwind.config.js`)

```js
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      keyframes: {
        'fade-in': {
          '0%': { opacity: '0', transform: 'translateY(4px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      animation: {
        'fade-in': 'fade-in 0.2s ease-out',
      },
    },
  },
  plugins: [],
};
```

---

## Variáveis de Ambiente

| Variável | Padrão | Descrição |
|---|---|---|
| `VITE_API_URL` | `http://localhost:8000` | URL base da API FastAPI |

---

## Propriedades de Correção (Property-Based Testing)

As seguintes propriedades formais devem ser satisfeitas pela implementação:

### P1 — Integridade do Histórico
Para qualquer sequência de N mensagens enviadas com sucesso, o histórico deve conter exatamente N pares (user + assistant), em ordem cronológica.

### P2 — Isolamento de Sessão
Para qualquer `session_id` gerado, ele deve ser um UUID v4 válido (formato `xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx`) e único por carregamento de página.

### P3 — Idempotência do Tema
Para qualquer número de alternâncias de tema, o estado final deve ser consistente com o número de cliques (par → tema inicial, ímpar → tema oposto) e refletido na classe do `<html>` e no `localStorage`.

### P4 — Invariante de Carregamento
Durante qualquer requisição em andamento (`isLoading = true`), o campo de entrada e o botão de envio devem estar desabilitados. Após a conclusão (sucesso ou erro), devem estar habilitados.

### P5 — Filtragem de Mensagens Vazias
Para qualquer string composta exclusivamente de espaços em branco ou vazia, nenhuma requisição à API deve ser disparada.

### P6 — Preservação de Fontes
Para qualquer resposta da API que contenha `sources`, cada `SourceReference` deve ser exibida abaixo da mensagem correspondente, sem perda ou reordenação.
