import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { DailyPoint } from '../../types/analytics';

export default function LatencyChart({ data }: { data: DailyPoint[] }) {
  return (
    <div className="glass rounded-card p-5">
      <h3 className="font-display text-ink mb-4">Latency</h3>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.08)" />
          <XAxis dataKey="label" stroke="#64748B" fontSize={12} />
          <YAxis stroke="#64748B" fontSize={12} />
          <Tooltip contentStyle={{ background: '#141F38', border: '1px solid rgba(148,163,184,0.2)', borderRadius: 12 }} />
          <Line type="monotone" dataKey="latency" stroke="#22D3EE" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
