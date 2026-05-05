import { useState } from 'react';
import { getDocumentDownloadUrl } from '../services/api';
import { useDocuments } from '../hooks/useDocuments';

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function FileIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="14"
      height="14"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      className="shrink-0 text-indigo-500 dark:text-indigo-400"
    >
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
    </svg>
  );
}

function DownloadIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="13"
      height="13"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="7 10 12 15 17 10" />
      <line x1="12" y1="15" x2="12" y2="3" />
    </svg>
  );
}

function CloseIcon() {
  return (
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
    >
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  );
}

export default function DocumentsSidebar() {
  const [isOpen, setIsOpen] = useState(false);
  const { documents, isLoading, error, reload } = useDocuments();

  return (
    <>
      {/* Barra lateral estreita com o botão */}
      <aside
        aria-label="Navegação lateral"
        className="w-12 shrink-0 flex flex-col items-center pt-3 gap-2
          border-r border-gray-200 dark:border-gray-700
          bg-white dark:bg-gray-900"
      >
        <button
          onClick={() => setIsOpen(true)}
          aria-label="Abrir painel de documentos"
          title="Documentos"
          className={`w-9 h-9 rounded-lg flex items-center justify-center transition-colors
            ${isOpen
              ? 'bg-indigo-100 dark:bg-indigo-900 text-indigo-600 dark:text-indigo-400'
              : 'text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800'
            }`}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
          </svg>
        </button>
      </aside>

      {/* Overlay escuro ao abrir o painel */}
      {isOpen && (
        <div
          className="fixed inset-0 z-20 bg-black/20 dark:bg-black/40"
          onClick={() => setIsOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* Drawer de documentos */}
      <div
        role="dialog"
        aria-label="Painel de documentos"
        aria-modal="true"
        className={`fixed top-0 left-12 h-full w-64 z-30 flex flex-col
          bg-white dark:bg-gray-900
          border-r border-gray-200 dark:border-gray-700
          shadow-xl
          transition-transform duration-200 ease-out
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}`}
      >
        {/* Cabeçalho do drawer */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="15"
              height="15"
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
            <span className="text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
              Documentos
            </span>
          </div>
          <button
            onClick={() => setIsOpen(false)}
            aria-label="Fechar painel de documentos"
            className="w-7 h-7 rounded-lg flex items-center justify-center
              text-gray-400 dark:text-gray-500
              hover:bg-gray-100 dark:hover:bg-gray-800
              hover:text-gray-600 dark:hover:text-gray-300
              transition-colors"
          >
            <CloseIcon />
          </button>
        </div>

        {/* Conteúdo do drawer */}
        <div className="flex-1 overflow-y-auto px-2 py-2">
          {/* Loading */}
          {isLoading && (
            <div className="flex items-center justify-center py-10">
              <div className="w-4 h-4 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            </div>
          )}

          {/* Erro */}
          {!isLoading && error && (
            <div className="px-2 py-4 text-center">
              <p className="text-xs text-red-600 dark:text-red-400 mb-2">{error}</p>
              <button
                onClick={reload}
                className="text-xs text-indigo-600 dark:text-indigo-400 hover:underline"
              >
                Tentar novamente
              </button>
            </div>
          )}

          {/* Lista vazia */}
          {!isLoading && !error && documents.length === 0 && (
            <p className="text-xs text-gray-400 dark:text-gray-500 text-center py-10 px-2">
              Nenhum documento disponível.
            </p>
          )}

          {/* Lista de documentos */}
          {!isLoading && !error && documents.length > 0 && (
            <ul className="space-y-0.5">
              {documents.map((doc) => (
                <li key={doc.filename}>
                  <a
                    href={getDocumentDownloadUrl(doc.filename)}
                    download={doc.filename}
                    aria-label={`Baixar ${doc.filename}`}
                    className="group flex items-start gap-2 w-full rounded-lg px-2 py-2
                      hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                  >
                    <FileIcon />
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium text-gray-800 dark:text-gray-200 truncate leading-tight">
                        {doc.filename}
                      </p>
                      <p className="text-[11px] text-gray-400 dark:text-gray-500 mt-0.5">
                        {formatSize(doc.size_bytes)}
                      </p>
                    </div>
                    <span className="shrink-0 text-gray-400 dark:text-gray-500
                      group-hover:text-indigo-500 dark:group-hover:text-indigo-400
                      transition-colors mt-0.5">
                      <DownloadIcon />
                    </span>
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
