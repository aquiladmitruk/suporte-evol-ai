# Documento de Requisitos — Painel de Documentos

## Introdução

Este documento descreve os requisitos funcionais e não funcionais da feature **Painel de Documentos** do Assistente de IA do ERP Evol. A feature adiciona uma sidebar lateral esquerda à interface existente, exibindo a lista de arquivos disponíveis na pasta `backend/documents/` e permitindo o download de cada arquivo diretamente pelo navegador. O backend expõe dois novos endpoints REST para listar e servir os arquivos. A feature deve integrar-se ao layout e ao sistema de temas (claro/escuro) já existentes na aplicação.

## Glossário

| Termo | Definição |
|---|---|
| **Aplicação** | A interface web do Assistente de IA do ERP Evol |
| **Sidebar** | Painel lateral esquerdo da interface que exibe a seção de Documentos |
| **Documento** | Arquivo disponibilizado na pasta `backend/documents/` para download pelos usuários |
| **API** | O serviço backend FastAPI que processa as requisições e serve os arquivos |
| **DocumentoRouter** | Módulo FastAPI responsável pelos endpoints de listagem e download de Documentos |
| **DocumentoService** | Módulo de lógica de negócio responsável por listar e servir arquivos da pasta `backend/documents/` |
| **DocumentoItem** | Tipo de dado que representa um Documento disponível, contendo `filename` (string) e `size_bytes` (number) |
| **DocumentoListResponse** | Tipo de dado retornado pelo endpoint de listagem, contendo uma lista de `DocumentoItem` |
| **Pasta de Documentos** | Diretório `backend/documents/` onde os arquivos são armazenados manualmente pelo administrador |
| **Usuário** | Pessoa que interage com a interface do Assistente de IA do ERP Evol |
| **Tema** | Esquema visual da interface: Claro (Light) ou Escuro (Dark) |

---

## Requisitos

### Requisito 1: Endpoint de Listagem de Documentos

**User Story:** Como Usuário, quero que o backend liste os arquivos disponíveis para download, para que o frontend possa exibir a lista atualizada de Documentos.

#### Critérios de Aceitação

1. THE DocumentoRouter SHALL expor o endpoint `GET /api/documents` que retorna a lista de Documentos disponíveis na Pasta de Documentos.
2. WHEN o endpoint `GET /api/documents` é chamado, THE DocumentoService SHALL ler o conteúdo da Pasta de Documentos e retornar uma lista de `DocumentoItem` com os campos `filename` e `size_bytes` de cada arquivo encontrado.
3. WHEN a Pasta de Documentos estiver vazia, THE DocumentoRouter SHALL retornar uma lista vazia com status HTTP 200.
4. IF a Pasta de Documentos não existir no sistema de arquivos, THEN THE DocumentoRouter SHALL retornar uma lista vazia com status HTTP 200, sem lançar erro.
5. THE DocumentoRouter SHALL ignorar subdiretórios dentro da Pasta de Documentos, listando apenas arquivos regulares.
6. THE DocumentoRouter SHALL retornar os itens da lista em ordem alfabética pelo campo `filename`.

---

### Requisito 2: Endpoint de Download de Documentos

**User Story:** Como Usuário, quero fazer o download de um Documento específico pelo nome do arquivo, para que eu possa acessar o conteúdo localmente.

#### Critérios de Aceitação

1. THE DocumentoRouter SHALL expor o endpoint `GET /api/documents/{filename}` que serve o arquivo correspondente para download.
2. WHEN o endpoint `GET /api/documents/{filename}` é chamado com um `filename` existente na Pasta de Documentos, THE DocumentoService SHALL retornar o conteúdo binário do arquivo com o cabeçalho `Content-Disposition: attachment; filename="{filename}"`.
3. IF o `filename` solicitado não existir na Pasta de Documentos, THEN THE DocumentoRouter SHALL retornar status HTTP 404 com mensagem de erro descritiva.
4. IF o `filename` solicitado contiver sequências de travessia de diretório (ex.: `../`, `..\\`), THEN THE DocumentoRouter SHALL retornar status HTTP 400 com mensagem de erro descritiva, sem acessar o sistema de arquivos fora da Pasta de Documentos.
5. THE DocumentoService SHALL detectar automaticamente o tipo MIME do arquivo com base na extensão e incluí-lo no cabeçalho `Content-Type` da resposta.
6. THE DocumentoRouter SHALL suportar arquivos de qualquer tipo (PDF, DOCX, XLSX, imagens, texto, etc.).

---

### Requisito 3: Integração do DocumentoRouter na Aplicação FastAPI

**User Story:** Como desenvolvedor, quero que os novos endpoints de documentos sejam registrados na aplicação FastAPI existente, para que fiquem acessíveis sob o prefixo `/api`.

#### Critérios de Aceitação

1. THE API SHALL registrar o DocumentoRouter com o prefixo `/api`, tornando os endpoints `GET /api/documents` e `GET /api/documents/{filename}` acessíveis.
2. THE API SHALL aplicar as mesmas configurações de CORS já existentes aos novos endpoints do DocumentoRouter.

---

### Requisito 4: Sidebar de Documentos no Frontend

**User Story:** Como Usuário, quero ver uma sidebar lateral esquerda com a seção "Documentos", para que eu possa acessar os arquivos disponíveis sem sair da interface de chat.

#### Critérios de Aceitação

1. THE Aplicação SHALL exibir uma Sidebar fixa à esquerda do layout principal, contendo a seção "Documentos".
2. THE Aplicação SHALL adaptar o layout existente (`flex flex-col h-screen`) para um layout com Sidebar à esquerda e área de chat à direita, mantendo o Header no topo.
3. WHILE o Tema Escuro estiver ativo, THE Sidebar SHALL aplicar as cores do dark mode consistentes com o restante da interface (fundo `gray-900`, bordas `gray-700`, texto `gray-100`).
4. WHILE o Tema Claro estiver ativo, THE Sidebar SHALL aplicar as cores do light mode consistentes com o restante da interface (fundo `white`, bordas `gray-200`, texto `gray-900`).
5. THE Sidebar SHALL exibir um título ou ícone identificando a seção "Documentos".

---

### Requisito 5: Listagem de Documentos na Sidebar

**User Story:** Como Usuário, quero ver a lista de arquivos disponíveis na Sidebar, para que eu saiba quais Documentos posso baixar.

#### Critérios de Aceitação

1. WHEN a Aplicação é carregada, THE Sidebar SHALL realizar uma requisição `GET /api/documents` e exibir a lista de Documentos retornada.
2. WHEN a lista de Documentos é carregada com sucesso, THE Sidebar SHALL exibir o `filename` de cada `DocumentoItem` na lista.
3. WHEN a lista de Documentos estiver vazia, THE Sidebar SHALL exibir uma mensagem informando que não há documentos disponíveis.
4. WHILE a requisição de listagem estiver em andamento, THE Sidebar SHALL exibir um indicador visual de carregamento.
5. IF a requisição de listagem falhar por erro de rede ou resposta HTTP não-2xx, THEN THE Sidebar SHALL exibir uma mensagem de erro amigável e um botão para tentar novamente.
6. THE Sidebar SHALL exibir o tamanho de cada arquivo em formato legível (ex.: "245 KB", "1,2 MB") com base no campo `size_bytes`.

---

### Requisito 6: Download de Documentos pelo Frontend

**User Story:** Como Usuário, quero clicar em um Documento na Sidebar para fazer o download, para que eu possa acessar o arquivo localmente sem precisar navegar para outra página.

#### Critérios de Aceitação

1. WHEN o Usuário clica em um Documento na Sidebar, THE Aplicação SHALL iniciar o download do arquivo correspondente via requisição `GET /api/documents/{filename}`.
2. THE Aplicação SHALL acionar o download do arquivo no navegador utilizando o atributo `download` em um elemento `<a>` ou criando um link temporário via JavaScript, sem navegar para outra página.
3. THE Aplicação SHALL construir a URL de download a partir da variável de ambiente `VITE_API_URL`, utilizando `http://localhost:8000` como valor padrão.
4. IF o download falhar com status HTTP 404, THEN THE Aplicação SHALL exibir uma mensagem de erro informando que o arquivo não foi encontrado.
5. IF o download falhar com outro erro HTTP ou de rede, THEN THE Aplicação SHALL exibir uma mensagem de erro amigável ao Usuário.

---

### Requisito 7: Serviço de API de Documentos no Frontend

**User Story:** Como desenvolvedor, quero uma função de serviço dedicada para comunicação com os endpoints de documentos, para que a lógica de acesso à API fique centralizada e reutilizável.

#### Critérios de Aceitação

1. THE Aplicação SHALL definir a função `fetchDocuments(): Promise<DocumentoItem[]>` no módulo de serviços, que realiza a requisição `GET /api/documents` e retorna a lista de `DocumentoItem`.
2. THE Aplicação SHALL definir a função `getDocumentDownloadUrl(filename: string): string` no módulo de serviços, que retorna a URL completa para download do arquivo.
3. THE Aplicação SHALL definir o tipo TypeScript `DocumentoItem` com os campos `filename` (string) e `size_bytes` (number).
4. IF a requisição `fetchDocuments` retornar status HTTP não-2xx, THEN THE Aplicação SHALL lançar um `Error` com mensagem descritiva.

---

### Requisito 8: Acessibilidade da Sidebar

**User Story:** Como Usuário, quero que a Sidebar seja acessível por teclado e leitores de tela, para que a interface seja utilizável por pessoas com diferentes necessidades.

#### Critérios de Aceitação

1. THE Sidebar SHALL utilizar elemento semântico `<nav>` ou `<aside>` com `aria-label` descritivo (ex.: `"Painel de documentos"`).
2. THE Aplicação SHALL garantir que cada item de Documento na lista seja focável via teclado e ativável pela tecla `Enter` ou `Space`.
3. THE Aplicação SHALL incluir `aria-label` descritivo em cada botão ou link de download, identificando o nome do arquivo (ex.: `"Baixar manual-erp.pdf"`).
4. THE Sidebar SHALL manter contraste de cores adequado (mínimo WCAG AA) tanto no Tema Claro quanto no Tema Escuro.
