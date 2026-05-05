# Documento de Requisitos

## Introdução

Este documento descreve os requisitos funcionais e não funcionais do **Assistente de IA para Suporte do ERP Evol** — uma aplicação web conversacional (estilo ChatGPT) que permite a usuários do ERP Evol obter orientações operacionais de forma rápida e sem fricção, consultando uma base de conhecimento técnica e proprietária por meio de um pipeline RAG (Retrieval-Augmented Generation).

O sistema é composto por:
- Uma interface de chat web (frontend) acessível sem autenticação.
- Um backend em Python/FastAPI responsável pela orquestração das conversas e do pipeline RAG.
- Um banco de dados vetorial para armazenamento e busca semântica da documentação do ERP Evol.
- Scripts de ingestão para processar e indexar os documentos da base de conhecimento.

O assistente atua exclusivamente como consultor/educador: não executa ações, não insere dados e não altera configurações no ERP Evol.

---

## Glossário

- **Assistente**: A aplicação de IA conversacional descrita neste documento.
- **Usuário**: Qualquer pessoa que acessa a interface de chat do Assistente, sem necessidade de cadastro ou login.
- **Sessão**: Período de interação contínua do Usuário com o Assistente dentro de uma mesma aba do navegador, iniciada ao abrir a página e encerrada ao recarregar ou fechar a aba.
- **Mensagem**: Texto enviado pelo Usuário ou gerado pelo Assistente durante uma Sessão.
- **Histórico_de_Sessão**: Conjunto ordenado de Mensagens trocadas durante uma Sessão ativa, mantido exclusivamente em memória volátil.
- **Pipeline_RAG**: Fluxo de Recuperação e Geração Aumentada (Retrieval-Augmented Generation) que busca trechos relevantes da Base_de_Conhecimento antes de formular a resposta.
- **Base_de_Conhecimento**: Conjunto de documentos, manuais e tutoriais do ERP Evol indexados no Banco_Vetorial.
- **Banco_Vetorial**: Banco de dados dedicado ao armazenamento e busca por similaridade semântica de embeddings (ex.: Qdrant ou PGVector).
- **Embedding**: Representação vetorial numérica de um trecho de texto, gerada por um modelo de linguagem, usada para busca semântica.
- **Chunk**: Fragmento de texto extraído de um documento da Base_de_Conhecimento, utilizado como unidade de indexação no Banco_Vetorial.
- **LLM**: Modelo de Linguagem de Grande Escala (Large Language Model) utilizado para gerar as respostas do Assistente.
- **Script_de_Ingestão**: Rotina de linha de comando responsável por processar documentos e popular o Banco_Vetorial.
- **API**: Interface de Programação de Aplicação exposta pelo backend via FastAPI.
- **Tema**: Esquema visual da interface de chat (Claro ou Escuro).

---

## Requisitos

### Requisito 1: Interface de Chat Acessível sem Autenticação

**User Story:** Como Usuário, quero acessar o chat do Assistente diretamente pelo navegador sem precisar criar conta ou fazer login, para que eu possa obter ajuda sobre o ERP Evol de forma rápida e sem fricção.

#### Critérios de Aceitação

1. THE Assistente SHALL disponibilizar a interface de chat por meio de uma URL pública acessível via navegador web.
2. THE Assistente SHALL permitir que o Usuário inicie uma conversa sem exigir cadastro, login, autenticação ou qualquer credencial.
3. WHEN o Usuário acessa a URL do Assistente, THE Assistente SHALL exibir a interface de chat pronta para receber Mensagens em no máximo 3 segundos em condições normais de rede.
4. THE Assistente SHALL exibir uma área de entrada de texto e um botão de envio claramente identificados na interface de chat.
5. THE Assistente SHALL exibir o histórico de Mensagens da Sessão atual na área de conversa, ordenado cronologicamente do mais antigo ao mais recente.

---

### Requisito 2: Alternância de Tema Claro/Escuro

**User Story:** Como Usuário, quero alternar entre os temas Claro e Escuro na interface de chat, para que eu possa usar o Assistente confortavelmente em diferentes condições de iluminação.

#### Critérios de Aceitação

1. THE Assistente SHALL oferecer um controle visível na interface para alternar entre o Tema Claro e o Tema Escuro.
2. WHEN o Usuário aciona o controle de alternância de Tema, THE Assistente SHALL aplicar o novo Tema a toda a interface imediatamente, sem recarregar a página.
3. WHILE o Usuário permanece na mesma Sessão, THE Assistente SHALL manter o Tema selecionado ativo em todas as interações subsequentes.
4. THE Assistente SHALL respeitar a preferência de Tema do sistema operacional do Usuário como valor padrão inicial, utilizando o Tema Claro quando a preferência do sistema não puder ser detectada.

---

### Requisito 3: Envio e Recebimento de Mensagens

**User Story:** Como Usuário, quero enviar perguntas sobre o ERP Evol e receber respostas contextualizadas do Assistente, para que eu possa resolver minhas dúvidas operacionais de forma eficiente.

#### Critérios de Aceitação

1. WHEN o Usuário submete uma Mensagem, THE Assistente SHALL enviar a Mensagem ao backend e exibir um indicador visual de carregamento enquanto a resposta é processada.
2. WHEN o backend retorna a resposta, THE Assistente SHALL exibir a resposta na área de conversa em formato legível, suportando renderização de Markdown (negrito, itálico, listas e blocos de código).
3. WHEN o Usuário submete uma Mensagem com o campo de entrada vazio, THE Assistente SHALL manter o campo de entrada ativo sem enviar requisição ao backend.
4. IF o backend retornar um erro na requisição, THEN THE Assistente SHALL exibir uma mensagem de erro amigável ao Usuário, indicando que a resposta não pôde ser obtida e sugerindo tentar novamente.
5. THE Assistente SHALL permitir o envio de Mensagens tanto pelo clique no botão de envio quanto pelo pressionamento da tecla Enter.

---

### Requisito 4: Memória de Curto Prazo Volátil (Contexto de Sessão)

**User Story:** Como Usuário, quero que o Assistente lembre das mensagens anteriores da conversa atual, para que eu possa fazer perguntas de seguimento sem precisar repetir o contexto.

#### Critérios de Aceitação

1. WHILE uma Sessão está ativa, THE Assistente SHALL incluir o Histórico_de_Sessão completo em cada requisição ao LLM, respeitando o limite máximo de tokens do modelo utilizado.
2. WHILE uma Sessão está ativa, THE Assistente SHALL manter o Histórico_de_Sessão exclusivamente em memória volátil do servidor, sem persistir Mensagens em banco de dados relacional ou arquivo permanente.
3. WHEN a Sessão é encerrada (página recarregada ou aba fechada), THE Assistente SHALL descartar o Histórico_de_Sessão correspondente, tornando-o irrecuperável.
4. IF o Histórico_de_Sessão atingir o limite de tokens do LLM, THEN THE Assistente SHALL truncar as Mensagens mais antigas do histórico para acomodar novas Mensagens, preservando sempre a Mensagem mais recente do Usuário.

---

### Requisito 5: Pipeline RAG — Busca Semântica na Base de Conhecimento

**User Story:** Como Usuário, quero que o Assistente consulte a documentação oficial do ERP Evol antes de responder, para que as respostas sejam precisas, contextualizadas e baseadas em informações confiáveis do sistema.

#### Critérios de Aceitação

1. WHEN o backend recebe uma Mensagem do Usuário, THE Pipeline_RAG SHALL realizar uma busca semântica no Banco_Vetorial utilizando o texto da Mensagem como consulta.
2. WHEN a busca semântica retorna resultados, THE Pipeline_RAG SHALL selecionar os N Chunks mais relevantes (onde N é configurável via variável de ambiente, com valor padrão de 5) e incluí-los no contexto enviado ao LLM.
3. WHEN o LLM gera a resposta, THE Assistente SHALL basear a resposta prioritariamente nos Chunks recuperados, indicando ao LLM por meio do prompt do sistema que ele deve responder com base na documentação fornecida.
4. IF a busca semântica não retornar Chunks com similaridade acima do limiar mínimo configurado, THEN THE Assistente SHALL informar ao Usuário que não encontrou informações relevantes na Base_de_Conhecimento sobre o tema consultado.
5. THE Pipeline_RAG SHALL executar a busca semântica e obter a resposta do LLM em no máximo 15 segundos para 95% das requisições em condições normais de operação.

---

### Requisito 6: Script de Ingestão de Conhecimento

**User Story:** Como administrador do sistema, quero executar um script para processar e indexar documentos do ERP Evol no banco vetorial, para que a Base_de_Conhecimento esteja atualizada e disponível para o Assistente.

#### Critérios de Aceitação

1. THE Script_de_Ingestão SHALL aceitar como entrada um diretório contendo arquivos de documentação nos formatos PDF e TXT.
2. WHEN o Script_de_Ingestão processa um arquivo, THE Script_de_Ingestão SHALL dividir o conteúdo em Chunks de tamanho configurável (em número de tokens ou caracteres), com sobreposição (overlap) também configurável.
3. WHEN os Chunks são gerados, THE Script_de_Ingestão SHALL gerar um Embedding para cada Chunk utilizando o modelo de embeddings configurado e armazená-los no Banco_Vetorial com metadados de origem (nome do arquivo, número da página ou posição no documento).
4. IF um arquivo de entrada não puder ser lido ou processado, THEN THE Script_de_Ingestão SHALL registrar o erro em log com o nome do arquivo e a descrição do problema, e continuar o processamento dos demais arquivos.
5. WHEN o Script_de_Ingestão conclui a execução, THE Script_de_Ingestão SHALL exibir um relatório resumido indicando o número de arquivos processados com sucesso, o número de Chunks gerados e o número de erros encontrados.
6. THE Script_de_Ingestão SHALL ser idempotente: ao ser executado múltiplas vezes com os mesmos arquivos, THE Script_de_Ingestão SHALL atualizar os Chunks existentes no Banco_Vetorial em vez de criar duplicatas.

---

### Requisito 7: API do Backend (FastAPI)

**User Story:** Como desenvolvedor, quero que o backend exponha uma API bem definida via FastAPI, para que o frontend e outros clientes possam interagir com o Assistente de forma padronizada e confiável.

#### Critérios de Aceitação

1. THE API SHALL expor um endpoint de chat que aceite requisições HTTP POST contendo a Mensagem do Usuário e o Histórico_de_Sessão atual no corpo da requisição em formato JSON.
2. WHEN o endpoint de chat recebe uma requisição válida, THE API SHALL retornar a resposta do Assistente em formato JSON com código HTTP 200.
3. IF o corpo da requisição ao endpoint de chat estiver malformado ou ausente, THEN THE API SHALL retornar uma resposta com código HTTP 422 e uma descrição dos campos inválidos.
4. THE API SHALL expor um endpoint de verificação de saúde (health check) que retorne código HTTP 200 quando o serviço estiver operacional.
5. THE API SHALL expor documentação interativa automática (Swagger UI) acessível via navegador no caminho `/docs`.
6. THE API SHALL aplicar CORS (Cross-Origin Resource Sharing) permitindo requisições apenas das origens configuradas via variável de ambiente.

---

### Requisito 8: Escopo Restrito — Somente Consultivo

**User Story:** Como administrador do ERP Evol, quero garantir que o Assistente não possa executar ações no sistema ERP, para que não haja risco de alterações indevidas nos dados ou configurações do ERP Evol.

#### Critérios de Aceitação

1. THE Assistente SHALL responder exclusivamente com orientações textuais sobre o uso do ERP Evol, sem executar comandos, chamadas de API ou qualquer integração direta com o sistema ERP Evol.
2. WHEN o Usuário solicitar ao Assistente que execute uma ação no ERP Evol (ex.: "cadastre este fornecedor", "emita esta nota"), THE Assistente SHALL informar ao Usuário que sua função é exclusivamente orientativa e indicar o caminho no ERP Evol para que o Usuário realize a ação por conta própria.
3. THE Assistente SHALL incluir no prompt do sistema enviado ao LLM uma instrução explícita proibindo a geração de respostas que simulem a execução de ações no ERP Evol.

---

### Requisito 9: Configuração via Variáveis de Ambiente

**User Story:** Como operador de infraestrutura, quero que todas as configurações sensíveis e ajustáveis do sistema sejam gerenciadas por variáveis de ambiente, para que o Assistente possa ser implantado em diferentes ambientes sem alteração de código.

#### Critérios de Aceitação

1. THE Assistente SHALL ler as seguintes configurações exclusivamente de variáveis de ambiente: URL e credenciais do Banco_Vetorial, chave de API do LLM, modelo de LLM a ser utilizado, modelo de embeddings a ser utilizado, número máximo de Chunks recuperados (N), limiar mínimo de similaridade semântica e origens permitidas para CORS.
2. IF uma variável de ambiente obrigatória não estiver definida na inicialização do serviço, THEN THE Assistente SHALL encerrar a inicialização com código de saída diferente de zero e registrar em log quais variáveis estão ausentes.
3. THE Assistente SHALL disponibilizar um arquivo `.env.example` no repositório listando todas as variáveis de ambiente necessárias com descrições e valores de exemplo, sem conter valores reais de produção.
