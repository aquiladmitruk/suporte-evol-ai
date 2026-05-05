# Plano de Implementação — Painel de Documentos

## Tarefas

- [ ] 1. Criar pasta de documentos e estrutura de arquivos do backend
  - [ ] 1.1 Criar o diretório `backend/documents/` com arquivo `.gitkeep`
  - [ ] 1.2 Criar o arquivo `backend/app/routers/documents.py` com o `DocumentoRouter`
    - Implementar `GET /documents` com listagem ordenada alfabeticamente, ignorando subdiretórios
    - Implementar `GET /documents/{filename}` com proteção contra path traversal e detecção de MIME
    - Adicionar modelos Pydantic `DocumentoItem` e `DocumentoListResponse` (inline ou em `models.py`)
  - [ ] 1.3 Registrar o `DocumentoRouter` em `backend/app/main.py` com prefixo `/api`

- [ ] 2. Escrever testes de propriedade do backend (Hypothesis)
  - [ ] 2.1 Criar `backend/tests/property/test_documents_properties.py`
    - [ ] 2.1.1 [PBT] Propriedade 1 — Para qualquer conjunto de arquivos regulares, todos os DocumentoItem retornados têm filename não-vazio e size_bytes >= 0
    - [ ] 2.1.2 [PBT] Propriedade 2 — Para qualquer estrutura com subdiretórios, nenhum subdiretório aparece na resposta
    - [ ] 2.1.3 [PBT] Propriedade 3 — Para qualquer conjunto de arquivos, a lista retornada está em ordem alfabética
    - [ ] 2.1.4 [PBT] Propriedade 4 — Para qualquer filename contendo `../` ou `..\`, o endpoint retorna HTTP 400
    - [ ] 2.1.5 [PBT] Propriedade 5 — Para qualquer filename inexistente (sem path traversal), o endpoint retorna HTTP 404
    - [ ] 2.1.6 [PBT] Propriedade 6 — Para qualquer filename válido existente, a resposta contém Content-Disposition com o filename correto
    - [ ] 2.1.7 [PBT] Propriedade 7 — Para qualquer extensão conhecida, o Content-Type corresponde ao MIME type esperado

- [ ] 3. Escrever testes unitários do backend (exemplos concretos)
  - [ ] 3.1 Criar `backend/tests/unit/test_documents.py`
    - Pasta vazia → HTTP 200 com lista vazia
    - Pasta inexistente → HTTP 200 com lista vazia
    - Arquivo existente → conteúdo binário com Content-Disposition correto
    - Registro do router → endpoints acessíveis sob `/api`

- [ ] 4. Executar e validar testes do backend
  - Rodar `pytest backend/tests/` e garantir que todos os testes passam

- [ ] 5. Adicionar tipo `DocumentoItem` ao frontend
  - [ ] 5.1 Adicionar `DocumentoItem` e `DocumentoListResponse` em `frontend/src/types.ts`

- [ ] 6. Implementar funções de serviço no frontend
  - [ ] 6.1 Adicionar `fetchDocuments()` em `frontend/src/services/api.ts`
    - Realiza `GET /api/documents`, lança `Error` em status não-2xx, retorna `DocumentoItem[]`
  - [ ] 6.2 Adicionar `getDocumentDownloadUrl(filename: string): string` em `frontend/src/services/api.ts`
    - Retorna `${API_BASE_URL}/api/documents/${encodeURIComponent(filename)}`

- [ ] 7. Implementar hook `useDocuments`
  - [ ] 7.1 Criar `frontend/src/hooks/useDocuments.ts`
    - Estado: `documents`, `isLoading`, `error`, `refetch`
    - Chama `fetchDocuments()` no mount e a cada `refetch()`
    - Trata erros de rede e HTTP

- [ ] 8. Implementar componente `DocumentsSidebar`
  - [ ] 8.1 Criar `frontend/src/components/DocumentsSidebar.tsx`
    - Elemento `<aside>` com `aria-label="Painel de documentos"`, largura `w-64`
    - Estado de carregamento: skeleton/spinner
    - Estado de erro: mensagem + botão "Tentar novamente"
    - Estado vazio: mensagem "Nenhum documento disponível"
    - Estado com lista: renderiza cada `DocumentoItem` com ícone, filename, tamanho formatado e link de download
    - Cada link: `<a href={url} download aria-label="Baixar {filename}">`
    - Função utilitária `formatFileSize(bytes: number): string` (B / KB / MB)
    - Cores consistentes com dark mode (fundo `gray-900`, bordas `gray-700`, texto `gray-100`)

- [ ] 9. Atualizar layout em `App.tsx`
  - [ ] 9.1 Alterar o layout abaixo do `Header` de `flex-col` para `flex-row flex-1 overflow-hidden`
    - `<DocumentsSidebar />` à esquerda (largura fixa `w-64`)
    - `<main className="flex flex-col flex-1 overflow-hidden">` à direita com `ChatWindow` + `ChatInput`
  - [ ] 9.2 Importar e usar `DocumentsSidebar` em `App.tsx`

- [ ] 10. Escrever testes de propriedade do frontend (fast-check)
  - [ ] 10.1 Instalar dependências de teste: `vitest`, `@testing-library/react`, `@testing-library/jest-dom`, `jsdom`, `fast-check`
  - [ ] 10.2 Criar `frontend/src/services/__tests__/api.test.ts`
    - [ ] 10.2.1 [PBT] Propriedade 8 — Para qualquer size_bytes >= 0, formatFileSize retorna string não-vazia com unidade
    - [ ] 10.2.2 [PBT] Propriedade 9 — Para qualquer filename não-vazio, getDocumentDownloadUrl retorna URL com filename no path
    - [ ] 10.2.3 [PBT] Propriedade 10 — Para qualquer status HTTP 400–599, fetchDocuments lança Error

- [ ] 11. Escrever testes unitários do frontend (exemplos concretos)
  - [ ] 11.1 Criar `frontend/src/components/__tests__/DocumentsSidebar.test.tsx`
    - Renderiza skeleton durante carregamento
    - Renderiza lista de documentos após carregamento bem-sucedido
    - Renderiza mensagem de estado vazio quando lista está vazia
    - Renderiza mensagem de erro + botão retry em caso de falha
    - Botão retry chama `refetch`
    - Elemento `aside` tem `aria-label="Painel de documentos"`
    - Links de download têm `aria-label` descritivo com nome do arquivo

- [ ] 12. Executar e validar testes do frontend
  - Rodar `npm run test` (vitest --run) e garantir que todos os testes passam

- [ ] 13. Verificação final de integração
  - Iniciar backend e frontend, verificar que a sidebar exibe a lista de documentos
  - Verificar que o download funciona para arquivos PDF, DOCX e TXT
  - Verificar dark mode e light mode na sidebar
  - Verificar acessibilidade: navegação por teclado e aria-labels
