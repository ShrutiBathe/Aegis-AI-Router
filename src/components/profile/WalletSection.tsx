import { formatCurrency } from '../../utils/formatters';

export default function WalletSection({ balance }: { balance: number }) {
  return (
    <div className="glass rounded-card p-5">
      <p className="text-sm text-ink-muted mb-1">Wallet</p>
      <p className="font-display text-2xl text-ink">{formatCurrency(balance)}</p>
    </div>
  );
}
