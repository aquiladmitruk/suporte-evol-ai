import { SourceReference } from '../types';

interface SourceListProps {
  sources: SourceReference[];
}

export function SourceList({ sources }: SourceListProps) {
  if (!sources || sources.length === 0) {
    return null;
  }

  return (
    <div className="mt-2 pt-2 border-t border-gray-100 dark:border-gray-700">
      <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">Fontes:</p>
      <ul className="space-y-0.5">
        {sources.map((source, index) => (
          <li
            key={index}
            className="flex items-center gap-1.5 text-xs text-gray-500 dark:text-gray-400"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="12"
              height="12"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
            </svg>
            <span>
              {source.filename}
              {source.page !== undefined && ` · página ${source.page}`}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
