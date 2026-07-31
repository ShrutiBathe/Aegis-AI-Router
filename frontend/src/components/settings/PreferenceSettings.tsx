import { useState } from 'react';

export default function PreferenceSettings() {
  const [budget, setBudget] = useState(20);
  const [model, setModel] = useState('Gemini');
  return (
    <div className="glass rounded-card p-5 flex flex-col gap-4">
      <h3 className="font-display text-ink mb-1">Preferences</h3>
      <div>
        <p className="text-sm text-ink-muted mb-1">Default Budget: ₹{budget}</p>
        <input type="range" min={1} max={50} value={budget} onChange={(e) => setBudget(Number(e.target.value))} className="w-full accent-primary" />
      </div>
      <div>
        <p className="text-sm text-ink-muted mb-2">Preferred Models</p>
        <select value={model} onChange={(e) => setModel(e.target.value)} className="glass rounded-chip px-3 py-2 text-sm text-ink outline-none w-full">
          {['Gemini', 'Claude', 'GPT-4', 'Local AI'].map((m) => (
            <option key={m} value={m} className="bg-bg-soft">{m}</option>
          ))}
        </select>
      </div>
    </div>
  );
}
