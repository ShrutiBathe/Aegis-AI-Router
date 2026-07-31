import { useTasks } from '../../hooks/useTasks';
import { formatCurrency, timeAgo } from '../../utils/formatters';
import { classNames } from '../../utils/helpers';
import Loader from '../common/Loader';
import EmptyState from '../common/EmptyState';

const STATUS_STYLES: Record<string, string> = {
  completed: 'text-success bg-success/10 border-success/30',
  running: 'text-primary bg-primary/10 border-primary/30',
  queued: 'text-warning bg-warning/10 border-warning/30',
  failed: 'text-danger bg-danger/10 border-danger/30',
};

export default function RecentTasks() {
  const { tasks, loading } = useTasks();

  if (loading) return <Loader label="Loading recent tasks…" />;
  if (tasks.length === 0) return <EmptyState title="No tasks yet" description="Submit a task to see it routed here." />;

  return (
    <div className="glass rounded-card overflow-hidden">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-ink-faint border-b border-line">
            <th className="px-4 py-3 font-normal">Task</th>
            <th className="px-4 py-3 font-normal">Selected Agent</th>
            <th className="px-4 py-3 font-normal">Price</th>
            <th className="px-4 py-3 font-normal">Status</th>
            <th className="px-4 py-3 font-normal">Time</th>
          </tr>
        </thead>
        <tbody>
          {tasks.map((task) => (
            <tr key={task.id} className="border-b border-line last:border-0 hover:bg-white/5 transition">
              <td className="px-4 py-3 text-ink">{task.prompt}</td>
              <td className="px-4 py-3 text-ink-muted">{task.selectedAgent}</td>
              <td className="px-4 py-3 text-ink-muted">{formatCurrency(task.price)}</td>
              <td className="px-4 py-3">
                <span className={classNames('px-2.5 py-1 rounded-chip border text-xs capitalize', STATUS_STYLES[task.status])}>
                  {task.status}
                </span>
              </td>
              <td className="px-4 py-3 text-ink-faint">{timeAgo(task.createdAt)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
