export type ChatMessage = {
  role: 'user' | 'assistant';
  content: string;
};

export type ChatRequest = {
  session_id: string;
  message: string;
  history: ChatMessage[];
};

export type ChatResponse = {
  response: string;
  sources: SourceReference[];
};

export type SourceReference = {
  filename: string;
  page?: number;
};

// Tipo interno para mensagens com metadados de UI
export type UIMessage = ChatMessage & {
  id: string;
  sources?: SourceReference[];
  isError?: boolean;
};

// Painel de documentos
export type DocumentoItem = {
  filename: string;
  size_bytes: number;
};
