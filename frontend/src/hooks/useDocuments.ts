import { useState, useEffect, useCallback } from 'react';
import { fetchDocuments } from '../services/api';
import type { DocumentoItem } from '../types';

export function useDocuments(): {
  documents: DocumentoItem[];
  isLoading: boolean;
  error: string | null;
  reload: () => void;
} {
  const [documents, setDocuments] = useState<DocumentoItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await fetchDocuments();
      setDocuments(data);
    } catch {
      setError('Não foi possível carregar os documentos. Verifique sua conexão.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return { documents, isLoading, error, reload: load };
}
