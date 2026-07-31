import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { useAnalytics } from '../../hooks/useAnalytics';
import Loader from '../common/Loader';

export default function AnalyticsOverview() {
  const { daily, loading } = useAnalytics();
  if (loading) return <Loader label="Loading analytics…" />;

  return (
    <div className="glass rounded-card p-5">
      <h3 className="font-display text-ink mb-4">Tasks & Revenue, Last 7 Days</h3>
      <ResponsiveContainer width="100%" height={220}>
        <AreaChart data={daily}>
          <defs>
            <linearGradient id="taskGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#3B82F6" stopOpacity={0.5} />
              <stop offset="100%" stopColor="#3B82F6" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.08)" />
          <XAxis dataKey="label" stroke="#64748B" fontSize={12} />
          <YAxis stroke="#64748B" fontSize={12} />
          <Tooltip contentStyle={{ background: '#141F38', border: '1px solid rgba(148,163,184,0.2)', borderRadius: 12 }} />
          <Area type="monotone" dataKey="tasks" stroke="#3B82F6" fill="url(#taskGrad)" strokeWidth={2} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
