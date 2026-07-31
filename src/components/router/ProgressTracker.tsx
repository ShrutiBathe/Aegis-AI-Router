export default function ProgressTracker({ percent }: { percent: number }) {
  return (
    <div>
      <div className="flex justify-between text-xs text-ink-muted mb-1.5 font-mono">
        <span>Progress</span>
        <span>{percent}%</span>
      </div>
      <div className="h-2 w-full rounded-chip bg-white/5 overflow-hidden">
        <div
          className="h-full bg-grad-primary rounded-chip transition-all duration-500"
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  );
}
