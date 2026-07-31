export default function LiveLogs({ logs }: { logs: string[] }) {
  return (
    <div className="glass rounded-card p-4 h-64 overflow-y-auto font-mono text-xs">
      {logs.length === 0 && <p className="text-ink-faint">Waiting for task…</p>}
      {logs.map((log, i) => (
        <p key={i} className="text-ink-muted mb-1">
          <span className="text-success mr-2">✔</span>
          {log}
        </p>
      ))}
    </div>
  );
}
