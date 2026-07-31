import { useState } from 'react';
import { Eye, EyeOff, Copy } from 'lucide-react';

export default function APIKeySection({ apiKey }: { apiKey: string }) {
  const [visible, setVisible] = useState(false);
  return (
    <div className="glass rounded-card p-5">
      <p className="text-sm text-ink-muted mb-2">API Key</p>
      <div className="flex items-center gap-2">
        <code className="flex-1 bg-white/5 rounded-card px-3 py-2 text-xs text-ink font-mono truncate">
          {visible ? apiKey : '•'.repeat(20)}
        </code>
        <button onClick={() => setVisible((v) => !v)} className="text-ink-muted hover:text-ink">
          {visible ? <EyeOff size={16} /> : <Eye size={16} />}
        </button>
        <button onClick={() => navigator.clipboard.writeText(apiKey)} className="text-ink-muted hover:text-ink">
          <Copy size={16} />
        </button>
      </div>
    </div>
  );
}
