import { useEffect } from 'react';
import { getDocumentDownloadUrl } from '../services/api';
import { useDocuments } from '../hooks/useDocuments';

interface DocumentsDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function DocumentsDrawer({ isOpen, onClose }: DocumentsDrawerProps) {
  const { documents, isLoading, error, reload } = useDocuments();

  // Fechar com Escape
  useEffect(() => {
    if (!isOpen) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <>
      {/* Overlay */}
      <div
        className="fixed inset-0 z-40 bg-black/20 dark:bg-black/40"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Drawer */}
      <div
        role="dialog"
        aria-label="Painel de documentos"
        aria-modal="true"
        className="fixed top-0 left-56 h-full w-72 z-50 flex flex-col
          bg-white dark:bg-gray-900
          border-r border-gray-200 dark:border-gray-700
          shadow-2xl"
      >
        {/* Cabeçalho */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
              className="text-indigo-600 dark:text-indigo-400"
            >
              <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
            </svg>
            <span className="text-sm font-semibold text-gray-800 dark:text-gray-200">
              Documentos
            </span>
          </div>
          <button
            onClick={onClose}
            aria-label="Fechar painel de documentos"
            className="w-7 h-7 rounded-lg flex items-center justify-center
              text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300
              hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"
              fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
              aria-hidden="true">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        {/* Lista */}
        <div className="flex-1 overflow-y-auto px-2 py-2">
          {isLoading && (
            <div className="flex items-center justify-center py-12">
              <div className="w-5 h-5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            </div>
          )}

          {!isLoading && error && (
            <div className="text-center py-10 px-4">
              <p className="text-sm text-red-600 dark:text-red-400 mb-3">{error}</p>
              <button
                onClick={reload}
                className="text-sm text-indigo-600 dark:text-indigo-400 hover:underline"
              >
                Tentar novamente
              </button>
            </div>
          )}

          {!isLoading && !error && documents.length === 0 && (
            <p className="text-sm text-gray-400 dark:text-gray-500 text-center py-12 px-4">
              Nenhum documento disponível.
            </p>
          )}

          {!isLoading && !error && documents.length > 0 && (
            <ul className="space-y-0.5">
              {documents.map((doc) => (
                <li key={doc.filename}>
                  <a
                    href={getDocumentDownloadUrl(doc.filename)}
                    download={doc.filename}
                    aria-label={`Baixar ${doc.filename}`}
                    className="group flex items-center gap-3 rounded-lg px-3 py-2.5
                      hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                  >
                    {/* Ícone de arquivo */}
                    <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15"
                      viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
                      strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"
                      className="shrink-0 text-indigo-500 dark:text-indigo-400">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                      <polyline points="14 2 14 8 20 8" />
                    </svg>

                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-gray-800 dark:text-gray-200 truncate leading-tight">
                        {doc.filename}
                      </p>
                      <p className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">
                        {formatSize(doc.size_bytes)}
                      </p>
                    </div>

                    {/* Ícone de download — aparece no hover */}
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14"
                      viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
                      strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"
                      className="shrink-0 text-gray-300 dark:text-gray-600
                        group-hover:text-indigo-500 dark:group-hover:text-indigo-400
                        transition-colors">
                      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                      <polyline points="7 10 12 15 17 10" />
                      <line x1="12" y1="15" x2="12" y2="3" />
                    </svg>
                  </a>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </>
  );
}
