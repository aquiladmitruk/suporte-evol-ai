# Padrões de Código

## Nomenclatura

- **Componentes React**: PascalCase — `MessageBubble`, `ChatInput`, `SourceList`
- **Hooks customizados**: camelCase com prefixo `use` — `useChat`, `useTheme`
- **Funções utilitárias**: camelCase — `sendMessage`, `formatSource`
- **Tipos e interfaces**: PascalCase — `ChatMessage`, `SourceReference`
- **Constantes**: UPPER_SNAKE_CASE — `API_BASE_URL`, `STORAGE_KEY_THEME`
- **Arquivos de componente**: PascalCase — `MessageBubble.tsx`
- **Arquivos de hook/serviço**: camelCase — `useChat.ts`, `api.ts`

## Componentes

- Preferir componentes funcionais pequenos e focados em uma responsabilidade
- Extrair lógica de negócio para hooks customizados — componentes devem ser majoritariamente declarativos
- Props obrigatórias sem valor padrão; props opcionais com `?` e valor padrão quando possível
- Evitar prop drilling além de 2 níveis — considerar composição de componentes

```tsx
// ✅ Bom
interface MessageBubbleProps {
  message: ChatMessage;
  isLoading?: boolean;
}

export function MessageBubble({ message, isLoading = false }: MessageBubbleProps) { ... }

// ❌ Evitar
export function MessageBubble(props: any) { ... }
```

## Tratamento de Erros

- Sempre tratar erros de `fetch` com `try/catch`
- Verificar `response.ok` antes de chamar `response.json()`
- Exibir mensagens de erro em português, amigáveis ao usuário
- Nunca expor detalhes técnicos (stack trace, status code) diretamente na UI

```ts
// ✅ Padrão para chamadas à API
try {
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(`Erro ao obter resposta: ${response.status}`);
  }
  const data: ChatResponse = await response.json();
  return data;
} catch (error) {
  // Tratar erro de rede ou HTTP
  throw error;
}
```

## Acessibilidade

- Botões devem ter `aria-label` descritivo quando não possuem texto visível
- Imagens e ícones decorativos devem ter `aria-hidden="true"`
- Usar elementos semânticos HTML (`<main>`, `<header>`, `<section>`, `<button>`)
- O campo de entrada deve ter `aria-label` ou `<label>` associado
- Indicador de carregamento deve ter `role="status"` e `aria-live="polite"`

## Estilo e Formatação

- Indentação: 2 espaços
- Aspas simples para strings em TypeScript/JavaScript
- Ponto e vírgula ao final das instruções
- Trailing comma em objetos e arrays multilinha
- Máximo de 100 caracteres por linha (orientativo)
- Importações agrupadas: bibliotecas externas → módulos internos → tipos

```tsx
// ✅ Ordem de importações
import { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

import { MessageBubble } from './components/MessageBubble';
import { useChat } from './hooks/useChat';

import type { ChatMessage } from './types';
```

## Commits e Mensagens

- Mensagens de commit em português, no imperativo
- Formato: `tipo: descrição curta`
- Tipos: `feat`, `fix`, `style`, `refactor`, `docs`, `chore`
- Exemplos:
  - `feat: adicionar indicador de carregamento no chat`
  - `fix: corrigir scroll automático ao receber mensagem`
  - `style: ajustar cores das bolhas no tema escuro`
