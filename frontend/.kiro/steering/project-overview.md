# Visão Geral do Projeto

## O que é este projeto

Interface web do Assistente de IA do ERP Evol — uma SPA (Single Page Application) em React que oferece uma experiência de chat conversacional para usuários do ERP Evol. O frontend se comunica com uma API FastAPI já existente e exibe respostas geradas por IA com base na documentação do sistema.

## Backend (já implementado)

O backend está disponível e expõe:

- `POST /api/chat` — recebe `{ session_id, message, history }` e retorna `{ response, sources }`
- `GET /api/health` — health check

A URL base da API é configurada via variável de ambiente `VITE_API_URL` (padrão: `http://localhost:8000`).

## Stack Tecnológica

| Camada | Tecnologia |
|---|---|
| Framework | React 18+ com TypeScript |
| Build tool | Vite |
| Estilização | Tailwind CSS (dark mode via classe `dark` no `<html>`) |
| Markdown | `react-markdown` + `remark-gfm` |
| Estado | React hooks nativos (`useState`, `useEffect`, `useRef`) |
| HTTP | `fetch` nativo — sem axios |
| UUID | biblioteca `uuid` (v4) |

## Fora do Escopo

- Autenticação ou sistema de login
- Persistência de histórico entre sessões
- Upload de arquivos ou imagens
- WebSocket ou notificações push
- Internacionalização (i18n) — interface em português
- Testes automatizados (iteração futura)
