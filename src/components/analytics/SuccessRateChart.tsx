import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { DailyPoint } from '../../types/analytics';

export default function SuccessRateChart({ data }: { data: DailyPoint[] }) {
  return (
    <div className="glass rounded-card p-5">
      <h3 className="font-display text-ink mb-4">Success Rate</h3>
      <ResponsiveContainer width="100%" height={220}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="successGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#22C55E" stopOpacity={0.5} />
              <stop offset="100%" stopColor="#22C55E" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.08)" />
          <XAxis dataKey="label" stroke="#64748B" fontSize={12} />
          <YAxis domain={[90, 100]} stroke="#64748B" fontSize={12} />
          <Tooltip contentStyle={{ background: '#141F38', border: '1px solid rgba(148,163,184,0.2)', borderRadius: 12 }} />
          <Area type="monotone" dataKey="successRate" stroke="#22C55E" fill="url(#successGrad)" strokeWidth={2} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
