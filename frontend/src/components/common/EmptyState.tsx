interface EmptyStateProps {
  title: string;
  description?: string;
  action?: React.ReactNode;
}

export default function EmptyState({ title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-16 text-center border border-dashed border-line rounded-card">
      <h3 className="font-display text-ink">{title}</h3>
      {description && <p className="text-sm text-ink-muted max-w-sm">{description}</p>}
      {action}
    </div>
  );
}
