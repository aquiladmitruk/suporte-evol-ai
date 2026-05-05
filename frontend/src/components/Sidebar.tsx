import { useState } from 'react';
import DocumentsDrawer from './DocumentsDrawer';

interface SidebarProps {
  isOpen: boolean;
}

export default function Sidebar({ isOpen }: SidebarProps) {
  const [docsOpen, setDocsOpen] = useState(false);

  return (
    <>
      <aside
        aria-label="Menu lateral"
        className={`shrink-0 flex flex-col
          bg-gray-200 dark:bg-gray-800
          overflow-hidden
          transition-all duration-300 ease-in-out
          ${isOpen ? 'w-56' : 'w-0'}`}
      >
        <nav className="flex-1 px-2 py-3 space-y-0.5 min-w-[14rem]">
          <button
            onClick={() => setDocsOpen(true)}
            aria-label="Abrir documentos"
            className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm
              transition-colors text-left whitespace-nowrap
              ${docsOpen
                ? 'bg-indigo-600 text-white'
                : 'text-gray-600 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-white'
              }`}
          >
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
              className="shrink-0"
            >
              <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
            </svg>
            Documentos
          </button>
        </nav>
      </aside>

      <DocumentsDrawer isOpen={docsOpen} onClose={() => setDocsOpen(false)} />
    </>
  );
}
