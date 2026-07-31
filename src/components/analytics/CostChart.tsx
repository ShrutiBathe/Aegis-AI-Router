import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { AgentUsage } from '../../types/analytics';

const COLORS = ['#3B82F6', '#8B5CF6', '#22D3EE', '#F59E0B', '#22C55E'];

export default function CostChart({ data }: { data: AgentUsage[] }) {
  return (
    <div className="glass rounded-card p-5">
      <h3 className="font-display text-ink mb-4">Cost Distribution</h3>
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie data={data} dataKey="usage" nameKey="agent" innerRadius={50} outerRadius={80} paddingAngle={3}>
            {data.map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip contentStyle={{ background: '#141F38', border: '1px solid rgba(148,163,184,0.2)', borderRadius: 12 }} />
          <Legend wrapperStyle={{ fontSize: 11, color: '#94A3B8' }} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
