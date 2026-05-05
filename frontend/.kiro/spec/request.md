# Frontend — Assistente de IA para Suporte do ERP Evol

## Objetivo
Desenvolver a interface web do assistente conversacional do ERP Evol utilizando React. O frontend deve se comunicar com a API FastAPI já existente (`POST /api/chat`) e oferecer uma experiência de chat fluida, limpa e responsiva, inspirada no ChatGPT.

## Contexto
O backend já está implementado e expõe os seguintes endpoints:

- `POST /api/chat` — recebe `{ session_id, message, history }` e retorna `{ response, sources }`
- `GET /api/health` — health check

O frontend é uma aplicação React independente, servida separadamente do backend. A comunicação é feita via HTTP, com o endereço da API configurável por variável de ambiente (`VITE_API_URL`).

## Stack Tecnológica
- **Framework:** React 18+ com TypeScript
- **Build tool:** Vite
- **Estilização:** Tailwind CSS
- **Renderização de Markdown:** `react-markdown` com `remark-gfm`
- **Gerenciamento de estado:** React hooks nativos (`useState`, `useEffect`, `useRef`) — sem Redux ou Zustand
- **HTTP:** `fetch` nativo (sem axios)
- **Geração de UUID:** `uuid` (para o `session_id`)

## Funcionalidades Principais

### Interface de Chat
- Layout de página única (SPA), sem rotas adicionais
- Área de mensagens com scroll automático para a última mensagem
- Bolhas de mensagem diferenciadas visualmente para usuário e assistente
- Indicador de carregamento (typing indicator / spinner) enquanto aguarda resposta da API
- Campo de entrada de texto com botão de envio
- Envio por `Enter` (sem `Shift+Enter`) e por clique no botão
- Mensagens vazias ou somente espaços não devem disparar requisição

### Alternância de Tema Claro/Escuro
- Botão de toggle visível no header para alternar entre Light e Dark
- Detectar preferência do sistema operacional (`prefers-color-scheme`) como valor inicial
- Persistir a preferência do usuário no `localStorage` entre recarregamentos de página
- Implementar via classe CSS no elemento `<html>` (padrão Tailwind dark mode: `class`)

### Gerenciamento de Sessão
- Gerar um `session_id` UUID v4 ao iniciar a aplicação e armazená-lo no `sessionStorage`
- O `session_id` é enviado em todas as requisições ao backend
- Ao recarregar a página, o `session_id` é descartado e um novo é gerado, zerando a conversa

### Histórico de Mensagens
- Manter o histórico de mensagens no estado React (`useState`)
- Enviar o histórico completo (`history`) em cada requisição ao backend
- Exibir as mensagens em ordem cronológica (mais antigas no topo)

### Tratamento de Erros
- Exibir mensagem de erro amigável na área de chat quando a API retornar erro (4xx/5xx)
- Exibir mensagem de erro em caso de timeout ou falha de rede
- Não bloquear a interface após erro — o usuário deve poder tentar novamente

### Exibição de Fontes
- Quando a resposta do backend incluir `sources`, exibir as referências abaixo da mensagem do assistente (nome do arquivo e página, se disponível)

## Restrições e Premissas

- Sem sistema de login, autenticação ou gestão de usuários
- Sem persistência de histórico de conversas entre sessões
- A URL da API deve ser configurável via variável de ambiente `VITE_API_URL` (padrão: `http://localhost:8000`)
- O projeto deve ter um `README.md` com instruções de instalação e execução
- Código em TypeScript com tipagem adequada para os modelos da API (`ChatMessage`, `ChatRequest`, `ChatResponse`, `SourceReference`)

## Fora do Escopo
- Upload de arquivos ou imagens
- Notificações push ou WebSocket (a comunicação é request/response simples)
- Internacionalização (i18n) — a interface será em português
- Testes automatizados (podem ser adicionados em iteração futura)
