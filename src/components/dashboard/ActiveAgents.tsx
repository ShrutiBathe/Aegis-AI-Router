import { PIPELINE_STAGES } from '../../utils/constants';
import { classNames } from '../../utils/helpers';

// Router Health, shown as a mini static pipeline diagram rather than a plain
// status list, so it echoes the same visual language as the live Execution page.
const SERVICES: Array<{ label: string; healthy: boolean }> = [
  { label: 'Planner', healthy: true },
  { label: 'Registry', healthy: true },
  { label: 'Payment Engine', healthy: true },
  { label: 'Execution Engine', healthy: true },
  { label: 'Aggregator', healthy: false },
];

export default function ActiveAgents() {
  return (
    <div className="glass rounded-card p-5">
      <h3 className="font-display text-ink mb-4">Router Health</h3>
      <div className="flex flex-wrap gap-3">
        {SERVICES.map((svc) => (
          <div
            key={svc.label}
            className={classNames(
              'flex items-center gap-2 px-3 py-2 rounded-card border text-sm',
              svc.healthy ? 'border-success/30 bg-success/5 text-ink' : 'border-danger/30 bg-danger/5 text-ink'
            )}
          >
            <span className={classNames('h-2 w-2 rounded-full', svc.healthy ? 'bg-success' : 'bg-danger')} />
            {svc.label}
            <span className="text-xs text-ink-faint">{svc.healthy ? 'healthy' : 'offline'}</span>
          </div>
        ))}
      </div>
      <p className="text-xs text-ink-faint mt-3 font-mono">
        {PIPELINE_STAGES.map((s) => s.label).join(' → ')}
      </p>
    </div>
  );
}
