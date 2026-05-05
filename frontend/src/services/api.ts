import type { ChatRequest, ChatResponse, DocumentoItem } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`Erro na API: ${response.status}`);
  }

  return response.json() as Promise<ChatResponse>;
}

export async function fetchDocuments(): Promise<DocumentoItem[]> {
  const response = await fetch(`${API_BASE_URL}/api/documents`);

  if (!response.ok) {
    throw new Error(`Erro ao listar documentos: ${response.status}`);
  }

  return response.json() as Promise<DocumentoItem[]>;
}

export function getDocumentDownloadUrl(filename: string): string {
  return `${API_BASE_URL}/api/documents/${encodeURIComponent(filename)}`;
}
