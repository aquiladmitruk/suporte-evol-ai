# Assistente de IA do ERP Evol — Frontend

Interface web do Assistente de IA do ERP Evol, construída com React, TypeScript e Vite. Permite que usuários façam perguntas sobre o ERP Evol em linguagem natural e recebam respostas contextualizadas com base na documentação do sistema.

---

## Pré-requisitos

- [Node.js](https://nodejs.org/) **18 ou superior**
- **npm** (incluído com o Node.js)

---

## Instalação

Clone o repositório e instale as dependências:

```bash
# Na raiz do repositório
cd frontend
npm install
```

---

## Configuração de variáveis de ambiente

Copie o arquivo de exemplo e ajuste conforme necessário:

```bash
cp .env.example .env.local
```

Edite o arquivo `.env.local`:

| Variável       | Descrição                                      | Padrão                    |
|----------------|------------------------------------------------|---------------------------|
| `VITE_API_URL` | URL base da API do backend (FastAPI)           | `http://localhost:8000`   |

> **Atenção:** o arquivo `.env.local` não deve ser commitado no repositório. Ele já está listado no `.gitignore`.

---

## Scripts disponíveis

| Script              | Comando           | Descrição                                                                 |
|---------------------|-------------------|---------------------------------------------------------------------------|
| Servidor de dev     | `npm run dev`     | Inicia o servidor de desenvolvimento com hot-reload em `http://localhost:5173` |
| Build de produção   | `npm run build`   | Compila TypeScript e gera os arquivos otimizados na pasta `dist/`         |
| Preview do build    | `npm run preview` | Serve localmente o build de produção gerado em `dist/` para validação     |
| Lint                | `npm run lint`    | Executa o ESLint em todos os arquivos `.ts` e `.tsx`                      |

### Desenvolvimento

```bash
npm run dev
```

Acesse [http://localhost:5173](http://localhost:5173) no navegador.

### Build de produção

```bash
npm run build
```

Os arquivos estáticos serão gerados em `frontend/dist/`. Para validar o build antes de fazer deploy:

```bash
npm run preview
```

---

## Estrutura do projeto

```
frontend/
├── public/                  # Arquivos estáticos públicos (favicon, etc.)
├── src/
│   ├── components/          # Componentes React
│   │   ├── ChatInput.tsx    # Campo de entrada de mensagens
│   │   ├── ChatWindow.tsx   # Janela de exibição do histórico de chat
│   │   ├── Header.tsx       # Cabeçalho com toggle de tema claro/escuro
│   │   ├── MessageBubble.tsx# Bolha de mensagem (usuário e assistente)
│   │   ├── SourceList.tsx   # Lista de fontes/documentos referenciados
│   │   └── TypingIndicator.tsx # Indicador de "digitando..."
│   ├── hooks/
│   │   ├── useChat.ts       # Lógica de estado do chat e chamadas à API
│   │   └── useTheme.ts      # Gerenciamento de tema claro/escuro
│   ├── services/
│   │   └── api.ts           # Cliente HTTP para comunicação com o backend
│   ├── types.ts             # Tipos TypeScript compartilhados
│   ├── App.tsx              # Componente raiz da aplicação
│   ├── main.tsx             # Ponto de entrada do React
│   └── index.css            # Estilos globais e diretivas Tailwind
├── .env.example             # Exemplo de variáveis de ambiente
├── index.html               # Template HTML principal
├── package.json
├── tailwind.config.js       # Configuração do Tailwind CSS
├── tsconfig.json            # Configuração do TypeScript
└── vite.config.ts           # Configuração do Vite
```

---

## Stack tecnológica

| Tecnologia         | Versão   | Função                                      |
|--------------------|----------|---------------------------------------------|
| React              | 18       | Biblioteca de UI                            |
| TypeScript         | 5        | Tipagem estática                            |
| Vite               | 5        | Bundler e servidor de desenvolvimento       |
| Tailwind CSS       | 3        | Estilização utilitária com suporte a dark mode |
| react-markdown     | 9        | Renderização de Markdown nas respostas      |
| remark-gfm         | 4        | Suporte a tabelas e listas no Markdown      |
| uuid               | 9        | Geração de `session_id` único por sessão    |

---

## Backend

O frontend consome a API REST do backend FastAPI localizado em `../backend/`.

Para iniciar o backend, consulte o `README` em [`../backend/`](../backend/) ou execute:

```bash
cd ../backend
# Ative o ambiente virtual e instale as dependências
pip install -e .
# Inicie o servidor
uvicorn app.main:app --reload
```

O backend ficará disponível em `http://localhost:8000` por padrão, que é o valor configurado em `VITE_API_URL`.

---

## Build de produção

Após executar `npm run build`, os arquivos estáticos em `dist/` podem ser servidos por qualquer servidor HTTP estático (Nginx, Apache, Vercel, etc.).

Certifique-se de que a variável `VITE_API_URL` aponta para a URL pública do backend antes de gerar o build, pois ela é embutida nos arquivos durante a compilação:

```bash
VITE_API_URL=https://api.seu-dominio.com npm run build
```
