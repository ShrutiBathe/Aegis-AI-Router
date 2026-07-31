import { motion } from 'framer-motion';
import { Cpu, Wifi, ListChecks, Wallet, Timer, CheckCircle2 } from 'lucide-react';
import { formatCurrency, formatLatency, formatPercent } from '../../utils/formatters';

const STATS = [
  { label: 'Total Agents', value: '134', icon: Cpu },
  { label: 'Online Agents', value: '121', icon: Wifi },
  { label: 'Tasks Executed', value: '426', icon: ListChecks },
  { label: 'Total Payments', value: formatCurrency(642), icon: Wallet },
  { label: 'Average Latency', value: formatLatency(1005), icon: Timer },
  { label: 'Success Rate', value: formatPercent(98.6), icon: CheckCircle2 },
];

export default function StatsCards() {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-3">
      {STATS.map((stat, i) => (
        <motion.div
          key={stat.label}
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.05 }}
          className="glass glass-hover rounded-card p-4 flex flex-col gap-2"
        >
          <stat.icon size={16} className="text-primary" />
          <span className="font-display text-xl text-ink">{stat.value}</span>
          <span className="text-xs text-ink-muted">{stat.label}</span>
        </motion.div>
      ))}
    </div>
  );
}
