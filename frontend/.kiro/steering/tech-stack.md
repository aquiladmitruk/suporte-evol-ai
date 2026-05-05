# Stack e Convenções Técnicas

## TypeScript

- Sempre usar TypeScript — sem `any` implícito
- Definir tipos explícitos para todos os modelos de dados da API:

```ts
type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

type ChatRequest = {
  session_id: string;
  message: string;
  history: ChatMessage[];
};

type ChatResponse = {
  response: string;
  sources: SourceReference[];
};

type SourceReference = {
  filename: string;
  page?: number;
};
```

- Tipos de domínio ficam em `src/types.ts`
- Props de componentes devem ser tipadas com `interface` ou `type` local no arquivo do componente

## React

- React 18+ com hooks funcionais — sem class components
- Gerenciamento de estado exclusivamente com `useState`, `useEffect`, `useRef`
- Sem Redux, Zustand ou qualquer biblioteca de estado externo
- Componentes em `src/components/`, um arquivo por componente
- Nomear componentes em PascalCase, arquivos em PascalCase (ex: `MessageBubble.tsx`)
- Hooks customizados em `src/hooks/`, prefixados com `use` (ex: `useChat.ts`)

## Tailwind CSS

- Usar classes utilitárias do Tailwind diretamente no JSX — sem CSS modules ou styled-components
- Dark mode configurado via estratégia `class` no `tailwind.config.js`
- A classe `dark` é aplicada/removida no elemento `<html>` pelo hook de tema
- Evitar estilos inline (`style={{}}`) — preferir classes Tailwind

## Comunicação com a API

- Usar `fetch` nativo — sem axios ou outras bibliotecas HTTP
- A URL base vem de `import.meta.env.VITE_API_URL ?? "http://localhost:8000"`
- Toda lógica de chamada à API fica isolada em `src/services/api.ts`
- Tratar erros HTTP (status não-2xx) e erros de rede separadamente
- Nunca deixar a interface bloqueada após um erro

## Sessão e Armazenamento

- `session_id`: gerado com `uuid` v4, armazenado no `sessionStorage`
  - Novo UUID a cada carregamento de página (comportamento padrão do `sessionStorage`)
- Preferência de tema: armazenada no `localStorage` com a chave `theme`
  - Valores: `"light"` | `"dark"`
  - Fallback: `prefers-color-scheme` do sistema operacional

## Estrutura de Pastas

```
src/
  components/       # Componentes React
  hooks/            # Hooks customizados
  services/         # Comunicação com a API (api.ts)
  types.ts          # Tipos TypeScript compartilhados
  App.tsx           # Componente raiz
  main.tsx          # Entry point
```
