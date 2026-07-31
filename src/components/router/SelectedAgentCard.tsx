import { CheckCircle2 } from 'lucide-react';
import { Agent } from '../../types/agent';

export default function SelectedAgentCard({ agent, score }: { agent: Agent; score: number }) {
  const reasons = ['Cheapest', 'Fastest', 'Highest Accuracy'];
  return (
    <div className="glass rounded-card p-5">
      <h3 className="font-display text-ink mb-3">Selected Agent</h3>
      <div className="flex items-center gap-3 mb-4">
        <div
          className="h-10 w-10 rounded-card flex items-center justify-center font-display text-white text-sm"
          style={{ background: agent.avatarColor }}
        >
          {agent.name.slice(0, 1)}
        </div>
        <div>
          <p className="text-ink font-medium">{agent.name}</p>
          <p className="text-xs text-ink-faint">{agent.owner}</p>
        </div>
      </div>
      <div className="flex flex-col gap-1.5 mb-4">
        {reasons.map((r) => (
          <div key={r} className="flex items-center gap-2 text-sm text-ink-muted">
            <CheckCircle2 size={14} className="text-success" /> {r}
          </div>
        ))}
      </div>
      <div className="pt-3 border-t border-line flex items-center justify-between">
        <span className="text-xs text-ink-faint">Router Score</span>
        <span className="font-display text-xl text-gradient">{score}</span>
      </div>
    </div>
  );
}
