import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { AgentUsage } from '../../types/analytics';

export default function AgentUsageChart({ data }: { data: AgentUsage[] }) {
  return (
    <div className="glass rounded-card p-5">
      <h3 className="font-display text-ink mb-4">Most Used Agents</h3>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data} layout="vertical" margin={{ left: 24 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.08)" />
          <XAxis type="number" stroke="#64748B" fontSize={12} />
          <YAxis dataKey="agent" type="category" stroke="#64748B" fontSize={11} width={110} />
          <Tooltip contentStyle={{ background: '#141F38', border: '1px solid rgba(148,163,184,0.2)', borderRadius: 12 }} />
          <Bar dataKey="usage" fill="#3B82F6" radius={[0, 6, 6, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
