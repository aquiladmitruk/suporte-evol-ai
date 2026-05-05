# Plano de Implementação: Assistente de IA para Suporte do ERP Evol (Backend)

## Visão Geral

Implementação incremental do backend do assistente conversacional com pipeline RAG. O frontend está em repositório/pasta separada e não faz parte deste escopo. O foco aqui é a API FastAPI, os serviços de backend, o script de ingestão e os testes correspondentes.

## Tarefas

- [x] 1. Estrutura do projeto e configuração de ambiente
  - Criar a estrutura de diretórios do backend: `app/`, `tests/unit/`, `tests/property/`, `tests/integration/`, `scripts/`
  - Criar `pyproject.toml` com as dependências: `fastapi`, `uvicorn[standard]`, `pydantic`, `pydantic-settings`, `qdrant-client`, `openai`, `hypothesis`, `pytest`, `pytest-asyncio`, `pdfplumber`, `python-dotenv`, `tiktoken`, `httpx`
  - Criar o arquivo `.env.example` listando todas as variáveis de ambiente obrigatórias e opcionais com descrições e valores de exemplo, sem valores reais
  - Criar o módulo `app/config.py` que lê todas as variáveis de ambiente via `pydantic-settings`, valida a presença das obrigatórias e encerra o processo com código de saída 1 e log das variáveis ausentes caso alguma falte
  - _Requisitos: 9.1, 9.2, 9.3_

- [x] 2. Modelos de dados (Pydantic)
  - Criar `app/models.py` com todos os modelos Pydantic definidos no design: `ChatMessage`, `ChatRequest`, `ChatResponse`, `SourceReference`, `RetrievedChunk`, `Chunk`, `ChunkMetadata`
  - Garantir que `ChatRequest` valide `session_id` não vazio e `message` não vazio
  - _Requisitos: 7.1, 7.3_

- [x] 3. Implementar `SessionStore`
  - Criar `app/session_store.py` com a classe `SessionStore` conforme a interface do design
  - Implementar `get_history`, `append_message`, `clear_session` e `truncate_to_token_limit` com TTL automático por sessão
  - O truncamento deve remover as mensagens mais antigas preservando sempre a última mensagem do usuário
  - _Requisitos: 4.1, 4.2, 4.3, 4.4_

  - [ ]* 3.1 Escrever testes unitários para `SessionStore`
    - Verificar comportamento de TTL expirado
    - Verificar que sessão inexistente retorna lista vazia
    - Verificar que `clear_session` torna o histórico irrecuperável
    - _Requisitos: 4.2, 4.3_

  - [ ]* 3.2 Escrever teste de propriedade: ordenação cronológica do histórico
    - **Propriedade 1: Ordenação cronológica do histórico de mensagens**
    - **Valida: Requisito 1.5**
    - Usar `st.lists(chat_message_strategy())` para verificar que a ordem de inserção é preservada sem inversões ou omissões

  - [ ]* 3.3 Escrever teste de propriedade: descarte do histórico ao encerrar sessão
    - **Propriedade 6: Descarte do histórico ao encerrar sessão**
    - **Valida: Requisito 4.3**
    - Usar `st.uuids()` + `st.lists(chat_message_strategy())` para verificar que após `clear_session` o histórico retorna lista vazia

  - [ ]* 3.4 Escrever teste de propriedade: truncamento preserva a mensagem mais recente
    - **Propriedade 7: Truncamento preserva a mensagem mais recente**
    - **Valida: Requisito 4.4**
    - Usar `st.lists(chat_message_strategy(), min_size=1)` para verificar que a última mensagem do usuário está presente após truncamento e que o total de tokens está dentro do limite

- [x] 4. Implementar `EmbeddingService`
  - Criar `app/embedding_service.py` com a classe `EmbeddingService` conforme a interface do design
  - Implementar `embed(text)` e `embed_batch(texts)` usando o cliente OpenAI com o modelo configurado em `EMBEDDING_MODEL`
  - _Requisitos: 5.1, 6.3_

- [x] 5. Implementar `RAGService`
  - Criar `app/rag_service.py` com a classe `RAGService` conforme a interface do design
  - Implementar `retrieve_chunks(query)`: gerar embedding da query via `EmbeddingService`, buscar no Qdrant os top-K chunks acima do limiar de similaridade, retornar lista vazia quando nenhum chunk superar o limiar
  - _Requisitos: 5.1, 5.2, 5.4_

  - [ ]* 5.1 Escrever testes unitários para `RAGService`
    - Verificar comportamento quando RAG retorna lista vazia (nenhum chunk acima do limiar)
    - Verificar que chunks são ordenados por score decrescente
    - _Requisitos: 5.2, 5.4_

  - [ ]* 5.2 Escrever teste de propriedade: seleção de exatamente N chunks relevantes
    - **Propriedade 8: Seleção de exatamente N chunks relevantes**
    - **Valida: Requisito 5.2**
    - Usar `st.lists(chunk_strategy(), min_size=0)` com mock do Qdrant para verificar que o resultado contém `min(M, N)` chunks sem duplicatas

  - [ ]* 5.3 Escrever teste de propriedade: fallback quando similaridade abaixo do limiar
    - **Propriedade 9: Fallback quando similaridade abaixo do limiar**
    - **Valida: Requisito 5.4**
    - Usar `st.floats(min_value=0.0, max_value=threshold)` para verificar que chunks abaixo do limiar resultam em lista vazia e prompt de fallback ao LLM

- [x] 6. Implementar `PromptBuilder`
  - Criar `app/prompt_builder.py` com a classe `PromptBuilder` conforme a interface do design
  - Implementar `build_system_prompt(retrieved_chunks)`: incluir os chunks recuperados no contexto e a instrução explícita que proíbe o LLM de simular execução de ações no ERP Evol
  - Implementar `build_messages(system_prompt, history, user_message)`: montar a lista de mensagens no formato esperado pelo LLM
  - _Requisitos: 5.3, 8.1, 8.3_

  - [ ]* 6.1 Escrever testes unitários para `PromptBuilder`
    - Verificar que o system prompt contém a instrução de restrição de escopo
    - Verificar que os chunks recuperados são incluídos no contexto do prompt
    - _Requisitos: 8.1, 8.3_

  - [ ]* 6.2 Escrever teste de propriedade: system prompt contém instrução de restrição de escopo
    - **Propriedade 16: System prompt contém instrução de restrição de escopo**
    - **Valida: Requisitos 8.1, 8.3**
    - Usar `st.lists(chunk_strategy())` para verificar que a instrução de restrição está presente em qualquer construção do prompt, independentemente dos chunks ou histórico

- [x] 7. Implementar `ChatService` e `LLMClient`
  - Criar `app/llm_client.py` com o cliente LLM (wrapper sobre o cliente OpenAI)
  - Criar `app/chat_service.py` com a classe `ChatService` conforme a interface do design
  - Implementar `process_message(session_id, user_message, client_history)`: orquestrar `SessionStore`, `RAGService`, `PromptBuilder` e `LLMClient`; incluir o histórico completo na requisição ao LLM; tratar o caso de lista vazia de chunks (fallback)
  - _Requisitos: 4.1, 5.3, 5.4, 8.2_

  - [ ]* 7.1 Escrever testes unitários para `ChatService`
    - Verificar comportamento quando RAG retorna lista vazia (deve incluir instrução de fallback no prompt)
    - Verificar tratamento de erro quando o LLM retorna falha (deve propagar erro adequado)
    - _Requisitos: 5.4, 8.2_

  - [ ]* 7.2 Escrever teste de propriedade: inclusão completa do histórico na requisição ao LLM
    - **Propriedade 5: Inclusão completa do histórico na requisição ao LLM**
    - **Valida: Requisito 4.1**
    - Usar `st.lists(chat_message_strategy(), max_size=50)` para verificar que o payload enviado ao LLM contém exatamente todas as N mensagens do histórico, na mesma ordem, sem omissões ou duplicações

- [x] 8. Implementar a API FastAPI
  - Criar `app/main.py` com a aplicação FastAPI: configurar CORS com as origens de `CORS_ALLOWED_ORIGINS`, registrar os routers de chat e health check
  - Criar `app/routers/chat.py` com o endpoint `POST /api/chat`: validar o payload via Pydantic (`ChatRequest`), chamar `ChatService.process_message`, retornar `ChatResponse` com HTTP 200; tratar erros do Qdrant (503) e do LLM (502)
  - Criar `app/routers/health.py` com o endpoint `GET /api/health` retornando HTTP 200
  - _Requisitos: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_

  - [ ]* 8.1 Escrever testes unitários para os endpoints da API
    - Verificar que `GET /api/health` retorna HTTP 200
    - Verificar que `POST /api/chat` com payload ausente retorna HTTP 422
    - _Requisitos: 7.3, 7.4_

  - [ ]* 8.2 Escrever teste de propriedade: aceitação de payloads válidos com HTTP 200
    - **Propriedade 13: Contrato de API — aceitação de payloads válidos**
    - **Valida: Requisitos 7.1, 7.2**
    - Usar `st.builds(ChatRequest, ...)` com TestClient do FastAPI para verificar que qualquer payload válido retorna HTTP 200 com campo `response`

  - [ ]* 8.3 Escrever teste de propriedade: rejeição de payloads inválidos com HTTP 422
    - **Propriedade 14: Rejeição de payloads inválidos com HTTP 422**
    - **Valida: Requisito 7.3**
    - Usar `st.fixed_dictionaries({...})` com campos obrigatórios ausentes ou de tipo incorreto para verificar que a API retorna HTTP 422 com descrição dos campos inválidos

  - [ ]* 8.4 Escrever teste de propriedade: aplicação de CORS por origem
    - **Propriedade 15: Aplicação de CORS por origem**
    - **Valida: Requisito 7.6**
    - Usar `st.lists(st.from_regex(url_pattern))` para verificar que apenas origens configuradas recebem o header `Access-Control-Allow-Origin`

- [x] 9. Implementar `TextChunker`
  - Criar `scripts/text_chunker.py` com a classe `TextChunker` conforme a interface do design
  - Implementar `chunk(text, metadata)`: dividir o texto em chunks de tamanho `chunk_size` com sobreposição `chunk_overlap` (em tokens via `tiktoken`), retornando lista de `Chunk` com metadados de origem
  - _Requisitos: 6.2_

  - [ ]* 9.1 Escrever testes unitários para `TextChunker`
    - Verificar chunking de texto vazio (deve retornar lista vazia)
    - Verificar chunking de texto menor que `chunk_size` (deve retornar um único chunk)
    - _Requisitos: 6.2_

  - [ ]* 9.2 Escrever teste de propriedade: chunking respeita tamanho e overlap configurados
    - **Propriedade 10: Chunking respeita tamanho e overlap configurados**
    - **Valida: Requisito 6.2**
    - Usar `st.text(min_size=1)` + `st.integers(min_value=1)` para verificar que todos os chunks têm comprimento ≤ `chunk_size` e que os últimos `chunk_overlap` tokens do chunk anterior aparecem no início do seguinte

- [x] 10. Implementar o script de ingestão
  - Criar `scripts/ingest.py` como CLI Python (usando `argparse`) que aceita um diretório de entrada
  - Criar `scripts/document_loader.py` com `DocumentLoader`: carregar arquivos PDF (via `pdfplumber`) e TXT do diretório informado
  - Integrar `DocumentLoader` → `TextChunker` → `EmbeddingService` → Qdrant (upsert com ID derivado de SHA-256 do conteúdo do chunk)
  - Implementar tratamento de erros por arquivo: registrar em log e continuar processando os demais
  - Exibir relatório final com número de arquivos processados, chunks gerados e erros encontrados
  - _Requisitos: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_

  - [ ]* 10.1 Escrever testes unitários para o script de ingestão
    - Verificar que arquivo ilegível é registrado em log e o processamento continua
    - Verificar que o relatório final reflete corretamente as contagens de sucesso e erro
    - _Requisitos: 6.4, 6.5_

  - [ ]* 10.2 Escrever teste de propriedade: resiliência a arquivos inválidos
    - **Propriedade 11: Resiliência do script de ingestão a arquivos inválidos**
    - **Valida: Requisitos 6.4, 6.5**
    - Usar `st.lists(file_strategy())` com mock do Qdrant para verificar que K arquivos válidos são processados, J erros são registrados e o relatório reflete exatamente essas contagens

  - [ ]* 10.3 Escrever teste de propriedade: idempotência da ingestão
    - **Propriedade 12: Idempotência da ingestão**
    - **Valida: Requisito 6.6**
    - Usar `st.lists(document_strategy())` com mock do Qdrant para verificar que N execuções com os mesmos arquivos produzem o mesmo número de chunks sem duplicatas acumuladas

- [x] 11. Checkpoint final — Verificar backend completo
  - Executar a suíte completa de testes unitários e de propriedade
  - Verificar que a API sobe corretamente com as variáveis de ambiente configuradas
  - Verificar que o script de ingestão processa documentos e popula o Qdrant corretamente

## Notas

- Tarefas marcadas com `*` são opcionais e podem ser puladas para uma entrega MVP mais rápida
- O frontend está em pasta separada e não é escopo deste plano
- Os testes de propriedade usam a biblioteca **Hypothesis** com no mínimo 100 iterações (`@settings(max_examples=100)`)
- Cada teste de propriedade deve ser anotado com o comentário: `# Feature: evol-erp-ai-assistant, Property N: <texto da propriedade>`
- O `SessionStore` usa memória volátil: em ambientes com múltiplas instâncias, sessões não são compartilhadas (tradeoff documentado no design)
- O ID de cada chunk no Qdrant é derivado de SHA-256 do conteúdo, garantindo idempotência via upsert
