# Documento de Requisitos — Frontend do Assistente de IA do ERP Evol

## Introdução

Este documento descreve os requisitos funcionais e não funcionais da interface web do Assistente de IA do ERP Evol. O frontend é uma Single Page Application (SPA) desenvolvida em React 18+ com TypeScript, que se comunica com a API FastAPI já existente para oferecer uma experiência de chat conversacional fluida, limpa e responsiva. A interface permite que usuários do ERP Evol façam perguntas em linguagem natural e recebam respostas contextualizadas com base na documentação do sistema.

## Glossário

| Termo | Definição |
|---|---|
| **Aplicação** | A interface web do Assistente de IA do ERP Evol |
| **Usuário** | Pessoa que interage com a interface de chat |
| **Assistente** | O agente de IA cujas respostas são exibidas na interface |
| **API** | O serviço backend FastAPI que processa as mensagens e retorna respostas |
| **Mensagem** | Texto enviado pelo Usuário ou pelo Assistente durante uma conversa |
| **Histórico** | Lista ordenada de todas as Mensagens trocadas na sessão atual |
| **Sessão** | Período de uso identificado por um `session_id` UUID v4 único, válido enquanto a aba do navegador estiver aberta |
| **Fonte** | Referência a um documento do ERP Evol citado pelo Assistente como base para sua resposta |
| **Tema** | Esquema visual da interface: Claro (Light) ou Escuro (Dark) |
| **ChatMessage** | Tipo TypeScript com campos `role` (`"user"` \| `"assistant"`) e `content` (string) |
| **ChatRequest** | Tipo TypeScript com campos `session_id` (string), `message` (string) e `history` (ChatMessage[]) |
| **ChatResponse** | Tipo TypeScript com campos `response` (string) e `sources` (SourceReference[]) |
| **SourceReference** | Tipo TypeScript com campo `filename` (string) e campo opcional `page` (number) |

---

## Requisitos

### Requisito 1: Layout e Estrutura da Interface de Chat

**User Story:** Como Usuário, quero uma interface de chat de página única com área de mensagens e campo de entrada, para que eu possa conversar com o Assistente de forma intuitiva.

#### Critérios de Aceitação

1. THE Aplicação SHALL renderizar uma única página sem rotas adicionais, contendo um cabeçalho (header), uma área de mensagens rolável e um campo de entrada de texto com botão de envio.
2. THE Aplicação SHALL exibir as Mensagens em ordem cronológica, com as mais antigas no topo e as mais recentes na parte inferior da área de mensagens.
3. THE Aplicação SHALL diferenciar visualmente as bolhas de Mensagem do Usuário das bolhas de Mensagem do Assistente por meio de cores, alinhamento e estilo distintos.
4. WHEN uma nova Mensagem é adicionada à área de mensagens, THE Aplicação SHALL rolar automaticamente a área de mensagens para exibir a Mensagem mais recente.
5. THE Aplicação SHALL ser responsiva, adaptando o layout para dispositivos móveis e desktops.

---

### Requisito 2: Envio de Mensagens

**User Story:** Como Usuário, quero enviar mensagens pressionando Enter ou clicando no botão de envio, para que eu possa interagir com o Assistente de forma ágil.

#### Critérios de Aceitação

1. WHEN o Usuário pressiona a tecla `Enter` (sem `Shift`) no campo de entrada, THE Aplicação SHALL enviar a Mensagem para a API.
2. WHEN o Usuário clica no botão de envio, THE Aplicação SHALL enviar a Mensagem para a API.
3. IF o campo de entrada contiver apenas espaços em branco ou estiver vazio, THEN THE Aplicação SHALL ignorar o evento de envio e não realizar requisição à API.
4. WHEN uma Mensagem é enviada, THE Aplicação SHALL limpar o campo de entrada de texto.
5. WHILE a Aplicação aguarda a resposta da API, THE Aplicação SHALL desabilitar o campo de entrada e o botão de envio para evitar envios duplicados.

---

### Requisito 3: Indicador de Carregamento

**User Story:** Como Usuário, quero ver um indicador visual enquanto o Assistente processa minha mensagem, para que eu saiba que a Aplicação está funcionando.

#### Critérios de Aceitação

1. WHILE a Aplicação aguarda a resposta da API após o envio de uma Mensagem, THE Aplicação SHALL exibir um indicador de carregamento (typing indicator ou spinner) na área de mensagens.
2. WHEN a resposta da API é recebida, THE Aplicação SHALL remover o indicador de carregamento e exibir a Mensagem do Assistente.

---

### Requisito 4: Comunicação com a API

**User Story:** Como Usuário, quero que minhas mensagens sejam enviadas ao backend com o histórico completo da conversa, para que o Assistente tenha contexto suficiente para responder com precisão.

#### Critérios de Aceitação

1. WHEN o Usuário envia uma Mensagem, THE Aplicação SHALL realizar uma requisição `POST` ao endpoint `/api/chat` com um corpo no formato `ChatRequest` contendo `session_id`, `message` e `history`.
2. THE Aplicação SHALL incluir o Histórico completo da Sessão atual no campo `history` de cada requisição enviada à API.
3. THE Aplicação SHALL utilizar o `fetch` nativo do navegador para realizar as requisições HTTP.
4. THE Aplicação SHALL ler a URL base da API a partir da variável de ambiente `VITE_API_URL`, utilizando `http://localhost:8000` como valor padrão quando a variável não estiver definida.
5. WHEN a API retorna uma resposta com status HTTP 2xx, THE Aplicação SHALL adicionar a resposta ao Histórico e exibi-la como Mensagem do Assistente.

---

### Requisito 5: Gerenciamento de Sessão

**User Story:** Como Usuário, quero que cada visita à Aplicação inicie uma nova sessão de conversa, para que conversas anteriores não interfiram na sessão atual.

#### Critérios de Aceitação

1. WHEN a Aplicação é carregada no navegador, THE Aplicação SHALL gerar um `session_id` UUID v4 único e armazená-lo no `sessionStorage` do navegador.
2. THE Aplicação SHALL incluir o `session_id` armazenado em todas as requisições enviadas à API durante a Sessão.
3. WHEN o Usuário recarrega a página, THE Aplicação SHALL descartar o `session_id` anterior, gerar um novo UUID v4 e iniciar o Histórico vazio.

---

### Requisito 6: Histórico de Mensagens

**User Story:** Como Usuário, quero que todas as mensagens da conversa sejam mantidas e exibidas durante a sessão, para que eu possa acompanhar o contexto da conversa.

#### Critérios de Aceitação

1. THE Aplicação SHALL manter o Histórico de Mensagens da Sessão atual no estado React utilizando o hook `useState`.
2. WHEN o Usuário envia uma Mensagem, THE Aplicação SHALL adicionar a Mensagem ao Histórico com `role` igual a `"user"` antes de realizar a requisição à API.
3. WHEN a API retorna uma resposta com sucesso, THE Aplicação SHALL adicionar a resposta ao Histórico com `role` igual a `"assistant"`.
4. THE Aplicação SHALL exibir todas as Mensagens do Histórico na área de mensagens em ordem cronológica.

---

### Requisito 7: Exibição de Fontes

**User Story:** Como Usuário, quero ver as referências documentais utilizadas pelo Assistente, para que eu possa consultar a documentação original do ERP Evol quando necessário.

#### Critérios de Aceitação

1. WHEN a resposta da API contém o campo `sources` com ao menos um item, THE Aplicação SHALL exibir as Fontes abaixo da Mensagem do Assistente correspondente.
2. THE Aplicação SHALL exibir o nome do arquivo (`filename`) de cada Fonte.
3. WHERE a Fonte contiver o campo `page`, THE Aplicação SHALL exibir o número da página junto ao nome do arquivo.
4. WHEN o campo `sources` da resposta da API estiver vazio ou ausente, THE Aplicação SHALL omitir a seção de Fontes abaixo da Mensagem do Assistente.

---

### Requisito 8: Renderização de Markdown

**User Story:** Como Usuário, quero que as respostas do Assistente sejam renderizadas com formatação Markdown, para que listas, títulos e trechos de código sejam exibidos de forma legível.

#### Critérios de Aceitação

1. WHEN a Mensagem do Assistente é exibida, THE Aplicação SHALL renderizar o conteúdo como Markdown utilizando a biblioteca `react-markdown` com o plugin `remark-gfm`.
2. THE Aplicação SHALL renderizar corretamente elementos Markdown como títulos, listas, negrito, itálico e blocos de código.

---

### Requisito 9: Tratamento de Erros

**User Story:** Como Usuário, quero ser informado quando ocorrer um erro na comunicação com o backend, para que eu saiba o que aconteceu e possa tentar novamente sem precisar recarregar a página.

#### Critérios de Aceitação

1. IF a API retornar uma resposta com status HTTP 4xx ou 5xx, THEN THE Aplicação SHALL exibir uma mensagem de erro amigável na área de mensagens.
2. IF a requisição à API falhar por timeout ou erro de rede, THEN THE Aplicação SHALL exibir uma mensagem de erro amigável na área de mensagens.
3. WHEN um erro é exibido, THE Aplicação SHALL reabilitar o campo de entrada e o botão de envio, permitindo que o Usuário tente novamente.
4. WHEN um erro ocorre, THE Aplicação SHALL remover o indicador de carregamento da área de mensagens.

---

### Requisito 10: Alternância de Tema Claro/Escuro

**User Story:** Como Usuário, quero alternar entre os temas Claro e Escuro e ter minha preferência salva, para que a interface respeite minha preferência visual entre recarregamentos de página.

#### Critérios de Aceitação

1. THE Aplicação SHALL exibir um botão de alternância de Tema visível no cabeçalho da interface.
2. WHEN a Aplicação é carregada, THE Aplicação SHALL verificar o `localStorage` para determinar o Tema preferido; IF nenhuma preferência estiver salva, THEN THE Aplicação SHALL utilizar a preferência do sistema operacional detectada via `prefers-color-scheme` como Tema inicial.
3. WHEN o Usuário clica no botão de alternância, THE Aplicação SHALL alternar entre os temas Claro e Escuro.
4. WHEN o Tema é alterado, THE Aplicação SHALL aplicar a classe `dark` ao elemento `<html>` quando o Tema Escuro estiver ativo, e removê-la quando o Tema Claro estiver ativo.
5. WHEN o Tema é alterado pelo Usuário, THE Aplicação SHALL persistir a preferência no `localStorage`.

---

### Requisito 11: Tipagem TypeScript

**User Story:** Como desenvolvedor, quero que os modelos de dados da API sejam tipados em TypeScript, para que o código seja seguro, legível e fácil de manter.

#### Critérios de Aceitação

1. THE Aplicação SHALL definir o tipo `ChatMessage` com os campos `role` (`"user"` | `"assistant"`) e `content` (string).
2. THE Aplicação SHALL definir o tipo `ChatRequest` com os campos `session_id` (string), `message` (string) e `history` (ChatMessage[]).
3. THE Aplicação SHALL definir o tipo `ChatResponse` com os campos `response` (string) e `sources` (SourceReference[]).
4. THE Aplicação SHALL definir o tipo `SourceReference` com o campo `filename` (string) e o campo opcional `page` (number).
5. THE Aplicação SHALL utilizar os tipos definidos em todos os componentes e funções que manipulam dados da API, sem uso de `any` implícito.

---

### Requisito 12: Documentação do Projeto

**User Story:** Como desenvolvedor, quero um README com instruções claras de instalação e execução, para que eu possa configurar o ambiente rapidamente.

#### Critérios de Aceitação

1. THE Aplicação SHALL incluir um arquivo `README.md` na raiz do projeto frontend com instruções de instalação, configuração de variáveis de ambiente e execução em desenvolvimento e produção.
