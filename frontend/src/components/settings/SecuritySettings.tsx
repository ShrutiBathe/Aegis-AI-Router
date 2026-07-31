export default function SecuritySettings() {
  return (
    <div className="glass rounded-card p-5">
      <h3 className="font-display text-ink mb-3">Privacy & API Tokens</h3>
      <button className="px-4 py-2 rounded-card text-sm border border-line text-ink-muted hover:text-ink transition">
        Regenerate API Token
      </button>
    </div>
  );
}
