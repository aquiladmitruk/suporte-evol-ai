# Assistente de IA para Suporte do ERP Evol

## Objetivo
Desenvolver uma aplicação web de suporte conversacional (estilo ChatGPT) capaz de tirar dúvidas e orientar usuários sobre o uso do sistema ERP "Evol", consultando uma base de conhecimento técnica e proprietária.

## Contexto e Casos de Uso
A aplicação será uma ferramenta de acesso rápido e sem fricção. O usuário abrirá a página, sem necessidade de login prévio, e fará perguntas operacionais como "Como emito uma nota fiscal de devolução no Evol?" ou "Onde configuro as alíquotas de imposto?". A IA manterá o contexto apenas das mensagens enviadas naquela mesma aba/sessão, permitindo perguntas de seguimento. Ao recarregar a página ou fechar o chat, a conversa é zerada, eliminando a necessidade de gerenciar históricos no banco de dados.

## Funcionalidades Principais (Core Features)
- **Interface de Chat (UI):** Frontend simples e limpo inspirado no ChatGPT, implementando alternância nativa entre temas Claro (Light) e Escuro (Dark).
- **Memória de Curto Prazo (Volátil):** O backend deve manter a janela de contexto da conversa apenas durante a sessão ativa (em memória ou cache temporário) para respostas coesas, descartando os dados ao fim da interação.
- **Pipeline RAG (Retrieval-Augmented Generation):** Integração com banco de dados vetorial para realizar buscas semânticas nos manuais, tutoriais e documentações do ERP Evol antes de formular a resposta final.
- **Scripts de Ingestão de Conhecimento:** Rotinas simples para processar os textos e manuais do Evol, gerando os *embeddings* necessários para alimentar o banco vetorial.

## Restrições e Premissas (Constraints)
- O backend deve ser construído em Python utilizando o framework FastAPI.
- A arquitetura RAG utilizará um banco de dados vetorial dedicado (como Qdrant ou PGVector) para armazenar e buscar a documentação do sistema.
- O sistema é *stateless* em relação ao usuário: nenhuma tabela de banco de dados relacional será criada para armazenar perfis, credenciais ou logs permanentes de chat.
- O escopo de atuação do assistente é estritamente consultivo/educativo; a IA não terá permissão para executar comandos, inserir dados ou alterar configurações diretamente no ERP Evol.

## Fora do Escopo (Out of Scope)
- Sistema de login, autenticação, autorização ou gestão de acessos (OAuth, JWT, senhas).
- Persistência e recuperação de histórico de conversas passadas.
- Diagnóstico avançado por imagem (análise de *prints* de tela do ERP).