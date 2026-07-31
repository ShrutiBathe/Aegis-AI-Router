import { Task } from '../../types/task';
import { formatCurrency, formatLatency } from '../../utils/formatters';
import PipelineFlow from '../router/PipelineFlow';

export default function TaskDetailsModal({ task, onClose }: { task: Task; onClose: () => void }) {
  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div className="glass rounded-card p-6 max-w-lg w-full" onClick={(e) => e.stopPropagation()}>
        <h3 className="font-display text-lg text-ink mb-4">{task.prompt}</h3>
        <PipelineFlow mode="idle" />
        <div className="grid grid-cols-2 gap-4 mt-5 text-sm">
          <div><p className="text-ink-faint text-xs">Agent</p><p className="text-ink">{task.selectedAgent}</p></div>
          <div><p className="text-ink-faint text-xs">Price</p><p className="text-ink">{formatCurrency(task.price)}</p></div>
          <div><p className="text-ink-faint text-xs">Status</p><p className="text-ink capitalize">{task.status}</p></div>
          <div><p className="text-ink-faint text-xs">Execution Time</p><p className="text-ink">{formatLatency(task.executionTimeMs)}</p></div>
        </div>
        <button onClick={onClose} className="mt-6 w-full py-2.5 rounded-chip bg-white/5 hover:bg-white/10 text-ink text-sm transition">
          Close
        </button>
      </div>
    </div>
  );
}
