# Tech Stack

## Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI with async/await throughout
- **Data validation**: Pydantic v2 (`BaseModel`, `field_validator`)
- **Settings**: `pydantic-settings` (`BaseSettings`) — all config via environment variables
- **Vector DB**: Qdrant (`qdrant-client` async client)
- **LLM**: OpenAI-compatible API (`openai` SDK)
- **Embeddings**: Configurable via `EMBEDDING_MODEL` env var
- **PDF parsing**: `pdfplumber`
- **Tokenization**: `tiktoken`
- **HTTP client**: `httpx`
- **Build**: `setuptools` / `pyproject.toml`

## Frontend
- **Language**: TypeScript (strict)
- **Framework**: React 18
- **Build tool**: Vite
- **Styling**: Tailwind CSS
- **Markdown rendering**: `react-markdown` + `remark-gfm`
- **Linting**: ESLint with `@typescript-eslint`

## Testing (Backend)
- **Runner**: pytest with `pytest-asyncio` (`asyncio_mode = "auto"`)
- **Property-based testing**: Hypothesis (`hypothesis==6.122.3`)
- Tests live in `backend/tests/` split into `unit/`, `property/`, and `integration/`

---

## Common Commands

### Backend
```bash
# Install dependencies (from backend/)
pip install -e ".[dev]"

# Run the dev server
uvicorn app.main:app --reload

# Run all tests
cd backend && pytest

# Run only unit tests
cd backend && pytest tests/unit

# Run only property tests
cd backend && pytest tests/property

# Ingest documents into Qdrant
cd backend && python scripts/ingest.py
```

### Frontend
```bash
# Install dependencies (from frontend/)
npm install

# Dev server
npm run dev

# Production build
npm run build

# Lint
npm run lint
```

---

## Environment Variables

Required (backend will exit on startup if missing):
- `QDRANT_URL` — Qdrant instance URL
- `LLM_API_KEY` — API key for the LLM provider
- `LLM_MODEL` — Model name (e.g. `gpt-4o`)
- `EMBEDDING_MODEL` — Embedding model name
- `CORS_ALLOWED_ORIGINS` — Comma-separated list of allowed origins

Optional (with defaults):
- `QDRANT_API_KEY` — Qdrant auth key (default: none)
- `QDRANT_COLLECTION` — Collection name (default: `evol_docs`)
- `RAG_TOP_K` — Max chunks to retrieve (default: `5`)
- `RAG_SIMILARITY_THRESHOLD` — Min similarity score (default: `0.7`)
- `SESSION_TTL_SECONDS` — Session expiry (default: `3600`)
- `CHUNK_SIZE` — Tokens per chunk (default: `512`)
- `CHUNK_OVERLAP` — Overlap between chunks (default: `64`)

Frontend:
- `VITE_API_URL` — Backend base URL (default: `http://localhost:8000`)
