interface ErrorPageProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
}

export default function ErrorPage({
  title = 'Something broke in the pipeline',
  message = 'The router could not complete this request. Try again, or check the execution logs.',
  onRetry,
}: ErrorPageProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-4 py-20 text-center">
      <div className="h-12 w-12 rounded-full bg-danger/10 border border-danger/30 flex items-center justify-center text-danger font-display text-xl">!</div>
      <h2 className="font-display text-xl text-ink">{title}</h2>
      <p className="text-ink-muted max-w-md text-sm">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-2 px-5 py-2 rounded-chip bg-grad-primary text-white text-sm font-medium hover:opacity-90 transition"
        >
          Retry
        </button>
      )}
    </div>
  );
}
