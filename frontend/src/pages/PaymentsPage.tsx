import { usePayments } from '../hooks/usePayments';
import WalletCard from '../components/payments/WalletCard';
import PaymentHistory from '../components/payments/PaymentHistory';
import { formatCurrency } from '../utils/formatters';
import { useAuth } from '../hooks/useAuth';

export default function PaymentsPage() {
  const { payments } = usePayments();
  const { user } = useAuth();

  const totalPaid = payments.filter((p) => p.status === 'completed').reduce((sum, p) => sum + p.amount, 0);
  const pending = payments.filter((p) => p.status === 'pending').length;
  const completed = payments.filter((p) => p.status === 'completed').length;

  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-6">
      <h1 className="font-display text-2xl text-ink">Payments</h1>

      <div className="grid md:grid-cols-4 gap-4">
        <div className="md:col-span-1">
          <WalletCard balance={user?.wallet ?? 0} />
        </div>
        <div className="glass rounded-card p-5"><p className="text-xs text-ink-faint mb-1">Total Paid</p><p className="font-display text-xl text-ink">{formatCurrency(totalPaid)}</p></div>
        <div className="glass rounded-card p-5"><p className="text-xs text-ink-faint mb-1">Completed</p><p className="font-display text-xl text-ink">{completed}</p></div>
        <div className="glass rounded-card p-5"><p className="text-xs text-ink-faint mb-1">Pending</p><p className="font-display text-xl text-ink">{pending}</p></div>
      </div>

      <div>
        <h2 className="font-display text-lg text-ink mb-3">Recent Payments</h2>
        <PaymentHistory />
      </div>
    </div>
  );
}
