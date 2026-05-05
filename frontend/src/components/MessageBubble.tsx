import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { SourceList } from './SourceList';
import { UIMessage } from '../types';

interface MessageBubbleProps {
  message: UIMessage;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const { role, content, sources, isError } = message;

  if (role === 'user') {
    return (
      <div className="flex justify-end px-4 py-1">
        <div className="max-w-[75%] bg-indigo-600 dark:bg-indigo-500 text-white rounded-2xl rounded-br-sm px-4 py-2.5 text-sm animate-fade-in">
          {content}
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex justify-start px-4 py-1">
        <div className="max-w-[85%] bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-800 rounded-2xl rounded-bl-sm px-4 py-3 text-sm animate-fade-in">
          <div className="flex items-start gap-2 text-red-700 dark:text-red-300">
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
              className="mt-0.5 shrink-0"
            >
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
              <line x1="12" y1="9" x2="12" y2="13" />
              <line x1="12" y1="17" x2="12.01" y2="17" />
            </svg>
            <span>{content}</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start px-4 py-1">
      <div className="max-w-[85%] bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl rounded-bl-sm px-4 py-3 text-sm text-gray-900 dark:text-gray-100 animate-fade-in">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          className="prose prose-sm dark:prose-invert max-w-none"
        >
          {content}
        </ReactMarkdown>
        {sources && sources.length > 0 && <SourceList sources={sources} />}
      </div>
    </div>
  );
}
