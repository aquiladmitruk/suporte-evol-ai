export default function TypingIndicator() {
  return (
    <div
      role="status"
      aria-label="Assistente digitando..."
      className="flex justify-start px-4 py-1"
    >
      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl rounded-bl-sm px-4 py-3">
        <span className="sr-only">Assistente digitando...</span>
        <div className="flex items-center gap-1">
          <div
            className="w-2 h-2 rounded-full bg-gray-400 dark:bg-gray-500 animate-bounce"
            style={{ animationDelay: '0ms' }}
          />
          <div
            className="w-2 h-2 rounded-full bg-gray-400 dark:bg-gray-500 animate-bounce"
            style={{ animationDelay: '150ms' }}
          />
          <div
            className="w-2 h-2 rounded-full bg-gray-400 dark:bg-gray-500 animate-bounce"
            style={{ animationDelay: '300ms' }}
          />
        </div>
      </div>
    </div>
  );
}
