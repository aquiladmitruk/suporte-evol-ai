# Fluxo de Desenvolvimento

## Pré-requisitos

- Node.js 18+
- npm 9+ ou pnpm 8+

## Instalação e Execução

```bash
# Instalar dependências
npm install

# Iniciar servidor de desenvolvimento
npm run dev

# Build de produção
npm run build

# Preview do build
npm run preview
```

## Variáveis de Ambiente

Criar um arquivo `.env.local` na raiz do projeto frontend:

```env
VITE_API_URL=http://localhost:8000
```

- `VITE_API_URL`: URL base da API FastAPI. Padrão: `http://localhost:8000`
- Variáveis prefixadas com `VITE_` são expostas ao código cliente pelo Vite
- Nunca commitar `.env.local` — adicionar ao `.gitignore`

## Dependências Principais

```json
{
  "dependencies": {
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    "react-markdown": "^9.0.0",
    "remark-gfm": "^4.0.0",
    "uuid": "^9.0.0"
  },
  "devDependencies": {
    "@types/react": "^18.0.0",
    "@types/react-dom": "^18.0.0",
    "@types/uuid": "^9.0.0",
    "@vitejs/plugin-react": "^4.0.0",
    "autoprefixer": "^10.0.0",
    "postcss": "^8.0.0",
    "tailwindcss": "^3.0.0",
    "typescript": "^5.0.0",
    "vite": "^5.0.0"
  }
}
```

## Configuração do Tailwind

O `tailwind.config.js` deve ter `darkMode: 'class'` para que o dark mode funcione via classe no `<html>`:

```js
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {},
  },
  plugins: [],
};
```

## Backend Local

Para rodar o backend localmente durante o desenvolvimento:

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

O frontend em `http://localhost:5173` se comunicará com o backend em `http://localhost:8000`.

## Build e Deploy

- O build gera arquivos estáticos em `dist/`
- O frontend pode ser servido por qualquer servidor HTTP estático (Nginx, Vercel, etc.)
- O backend deve estar acessível na URL configurada em `VITE_API_URL`
- Configurar CORS no backend para aceitar requisições da origem do frontend em produção
