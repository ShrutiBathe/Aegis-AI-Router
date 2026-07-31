import { useAnalytics } from '../hooks/useAnalytics';
import RevenueChart from '../components/analytics/RevenueChart';
import AgentUsageChart from '../components/analytics/AgentUsageChart';
import SuccessRateChart from '../components/analytics/SuccessRateChart';
import CostChart from '../components/analytics/CostChart';
import LatencyChart from '../components/analytics/LatencyChart';
import Loader from '../components/common/Loader';
import { formatCurrency, formatPercent } from '../utils/formatters';

export default function AnalyticsPage() {
  const { daily, usage, loading } = useAnalytics();
  if (loading) return <Loader label="Loading analytics…" />;

  const totalTasks = daily.reduce((sum, d) => sum + d.tasks, 0);
  const totalRevenue = daily.reduce((sum, d) => sum + d.revenue, 0);
  const avgCost = totalRevenue / totalTasks;
  const avgSuccess = daily.reduce((sum, d) => sum + d.successRate, 0) / daily.length;

  return (
    <div className="max-w-7xl mx-auto flex flex-col gap-6">
      <h1 className="font-display text-2xl text-ink">Analytics</h1>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="glass rounded-card p-4"><p className="text-xs text-ink-faint mb-1">Tasks</p><p className="font-display text-xl text-ink">{totalTasks}</p></div>
        <div className="glass rounded-card p-4"><p className="text-xs text-ink-faint mb-1">Revenue</p><p className="font-display text-xl text-ink">{formatCurrency(totalRevenue)}</p></div>
        <div className="glass rounded-card p-4"><p className="text-xs text-ink-faint mb-1">Average Cost</p><p className="font-display text-xl text-ink">{formatCurrency(Number(avgCost.toFixed(1)))}</p></div>
        <div className="glass rounded-card p-4"><p className="text-xs text-ink-faint mb-1">Success Rate</p><p className="font-display text-xl text-ink">{formatPercent(avgSuccess)}</p></div>
      </div>

      <div className="grid lg:grid-cols-2 gap-4">
        <RevenueChart data={daily} />
        <AgentUsageChart data={usage} />
        <SuccessRateChart data={daily} />
        <LatencyChart data={daily} />
        <CostChart data={usage} />
      </div>
    </div>
  );
}
