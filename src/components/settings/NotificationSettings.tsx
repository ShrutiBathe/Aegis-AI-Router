import { useState } from 'react';

export default function NotificationSettings() {
  const [enabled, setEnabled] = useState(true);
  return (
    <div className="glass rounded-card p-5">
      <h3 className="font-display text-ink mb-3">Notifications</h3>
      <label className="flex items-center justify-between text-sm text-ink-muted cursor-pointer">
        <span>Task and payment alerts</span>
        <input type="checkbox" checked={enabled} onChange={(e) => setEnabled(e.target.checked)} className="h-4 w-4 accent-primary" />
      </label>
    </div>
  );
}
