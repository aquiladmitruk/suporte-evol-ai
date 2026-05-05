# Project Structure

```
/
├── backend/                        # Python FastAPI backend
│   ├── app/
│   │   ├── main.py                 # App factory (create_app), CORS, router registration
│   │   ├── config.py               # Settings singleton via pydantic-settings (_LazySettings)
│   │   ├── models.py               # Pydantic v2 request/response models
│   │   ├── dependencies.py         # FastAPI dependency injection providers
│   │   ├── chat_service.py         # Orchestrates RAG → prompt → LLM → session pipeline
│   │   ├── rag_service.py          # Semantic search against Qdrant
│   │   ├── embedding_service.py    # Generates text embeddings
│   │   ├── llm_client.py           # OpenAI-compatible LLM calls
│   │   ├── prompt_builder.py       # Builds system prompt and message list for LLM
│   │   ├── session_store.py        # In-memory session history store
│   │   └── routers/
│   │       ├── chat.py             # POST /api/chat
│   │       ├── documents.py        # GET/POST /api/documents
│   │       └── health.py           # GET /api/health
│   ├── scripts/
│   │   ├── ingest.py               # Entry point: load + chunk + embed + upsert to Qdrant
│   │   ├── document_loader.py      # PDF loading via pdfplumber
│   │   └── text_chunker.py         # Token-aware text chunking (tiktoken)
│   ├── tests/
│   │   ├── unit/                   # Unit tests with fakes/stubs (no real I/O)
│   │   ├── property/               # Hypothesis property-based tests
│   │   └── integration/            # Integration tests (reserved)
│   ├── documents/                  # PDF files to ingest (gitignored except .gitkeep)
│   └── pyproject.toml
│
└── frontend/                       # React + TypeScript frontend
    ├── src/
    │   ├── App.tsx                 # Root layout: Header, Sidebar, ChatWindow, ChatInput
    │   ├── types.ts                # Shared TypeScript types (mirrors backend models)
    │   ├── components/             # UI components (Header, ChatWindow, ChatInput, etc.)
    │   ├── hooks/                  # Custom React hooks (useChat, useTheme)
    │   └── services/
    │       └── api.ts              # Fetch wrappers for all backend API calls
    ├── public/
    └── package.json
```

## Key Architectural Patterns

### Backend
- **Dependency injection**: Services are wired in `dependencies.py` and injected into routers via FastAPI `Depends()`. Never instantiate services directly inside routers.
- **Service layer**: Business logic lives in `*_service.py` files. Routers are thin — they validate input, call a service, and return the response.
- **Settings access**: Always import the `settings` singleton from `app.config`. Never read `os.environ` directly in application code.
- **Error handling**: Services raise `RuntimeError` for infrastructure failures (Qdrant, LLM). Routers catch these and return appropriate HTTP error responses.
- **Async**: All I/O-bound operations (Qdrant, LLM, embeddings) are `async`. Keep the pattern consistent.

### Testing
- **Unit tests** use hand-written fakes (e.g. `FakeRAGService`, `FakeLLMClient`) — no mocking frameworks in unit tests.
- **Property tests** use Hypothesis `@given` + `@settings`. Each property includes a comment referencing the requirement it validates (e.g. `# Valida: Requisito 5.2`).
- All async tests use `@pytest.mark.asyncio` (mode is `auto` so the marker is optional but kept for clarity).

### Frontend
- **Types**: `src/types.ts` mirrors backend Pydantic models. Keep them in sync when models change.
- **API calls**: All backend communication goes through `src/services/api.ts`. Components never call `fetch` directly.
- **State**: Chat state (messages, loading) is managed in the `useChat` hook. UI state (theme, sidebar) in dedicated hooks.
- **Styling**: Tailwind utility classes only — no separate CSS files except `index.css` for base styles.
