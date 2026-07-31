interface LoaderProps {
  label?: string;
}

export default function Loader({ label = 'Loading…' }: LoaderProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-12 text-ink-muted">
      <div className="h-8 w-8 rounded-full border-2 border-primary/30 border-t-primary animate-spin" />
      <span className="text-sm font-mono">{label}</span>
    </div>
  );
}
