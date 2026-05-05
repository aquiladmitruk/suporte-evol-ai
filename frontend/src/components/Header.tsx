interface HeaderProps {
  theme: 'light' | 'dark';
  onToggleTheme: () => void;
  sidebarOpen: boolean;
  onToggleSidebar: () => void;
}

export default function Header({ theme, onToggleTheme, sidebarOpen, onToggleSidebar }: HeaderProps) {
  return (
    <header className="flex items-center justify-between px-4 py-2.5
      bg-[#f3f4f6] dark:bg-gray-900">

      <div className="flex items-center gap-3">
        {/* Botão toggle sidebar */}
        <button
          onClick={onToggleSidebar}
          aria-label={sidebarOpen ? 'Recolher menu' : 'Expandir menu'}
          className="w-8 h-8 rounded-lg flex items-center justify-center
            text-gray-500 dark:text-gray-400
            hover:bg-gray-200 dark:hover:bg-gray-800 transition-colors"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24"
            fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"
            strokeLinejoin="round" aria-hidden="true">
            <line x1="3" y1="6" x2="21" y2="6" />
            <line x1="3" y1="12" x2="21" y2="12" />
            <line x1="3" y1="18" x2="21" y2="18" />
          </svg>
        </button>

        {/* Logo e título */}
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg bg-indigo-600 flex items-center justify-center shrink-0">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="white"
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
            </svg>
          </div>
          <span className="font-semibold text-gray-800 dark:text-white text-sm tracking-tight leading-tight">
            Assistente ERP Evol
          </span>
        </div>
      </div>

      {/* Toggle de tema */}
      <button
        onClick={onToggleTheme}
        aria-label={theme === 'light' ? 'Ativar tema escuro' : 'Ativar tema claro'}
        className="w-8 h-8 rounded-lg flex items-center justify-center
          text-gray-500 dark:text-gray-400
          hover:bg-gray-200 dark:hover:bg-gray-800 transition-colors"
      >
        {theme === 'light' ? (
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"
            fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"
            strokeLinejoin="round" aria-hidden="true">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
          </svg>
        ) : (
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"
            fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"
            strokeLinejoin="round" aria-hidden="true">
            <circle cx="12" cy="12" r="5" />
            <line x1="12" y1="1" x2="12" y2="3" />
            <line x1="12" y1="21" x2="12" y2="23" />
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
            <line x1="1" y1="12" x2="3" y2="12" />
            <line x1="21" y1="12" x2="23" y2="12" />
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
          </svg>
        )}
      </button>
    </header>
  );
}
