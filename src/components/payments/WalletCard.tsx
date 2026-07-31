import { Wallet } from 'lucide-react';
import { formatCurrency } from '../../utils/formatters';

export default function WalletCard({ balance }: { balance: number }) {
  return (
    <div className="glass rounded-card p-6 bg-grad-glow">
      <div className="flex items-center gap-2 text-ink-muted text-sm mb-2">
        <Wallet size={16} /> Wallet Balance
      </div>
      <p className="font-display text-3xl text-ink">{formatCurrency(balance)}</p>
    </div>
  );
}
