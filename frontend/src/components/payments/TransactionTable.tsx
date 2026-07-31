import { Payment } from '../../types/payment';
import { formatCurrency, timeAgo } from '../../utils/formatters';
import PaymentStatusBadge from './PaymentStatus';

export default function TransactionTable({ payments }: { payments: Payment[] }) {
  return (
    <div className="glass rounded-card overflow-x-auto">
      <table className="w-full text-sm min-w-[640px]">
        <thead>
          <tr className="text-left text-ink-faint border-b border-line">
            <th className="px-4 py-3 font-normal">Task</th>
            <th className="px-4 py-3 font-normal">Agent</th>
            <th className="px-4 py-3 font-normal">Stage</th>
            <th className="px-4 py-3 font-normal">Amount</th>
            <th className="px-4 py-3 font-normal">Algorand Tx</th>
            <th className="px-4 py-3 font-normal">Status</th>
            <th className="px-4 py-3 font-normal">Date</th>
          </tr>
        </thead>
        <tbody>
          {payments.map((p) => (
            <tr key={p.id} className="border-b border-line last:border-0 hover:bg-white/5 transition">
              <td className="px-4 py-3 text-ink">{p.taskName}</td>
              <td className="px-4 py-3 text-ink-muted">{p.agentName}</td>
              <td className="px-4 py-3 text-ink-faint text-xs font-mono">{p.stage}</td>
              <td className="px-4 py-3 text-ink-muted">{formatCurrency(p.amount)}</td>
              <td className="px-4 py-3 text-ink-faint font-mono text-xs">{p.algorandTxId}</td>
              <td className="px-4 py-3"><PaymentStatusBadge status={p.status} /></td>
              <td className="px-4 py-3 text-ink-faint">{timeAgo(p.date)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
