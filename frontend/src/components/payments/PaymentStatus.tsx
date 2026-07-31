import { classNames } from '../../utils/helpers';
import { PaymentStatus as Status } from '../../types/payment';

const STYLES: Record<Status, string> = {
  completed: 'text-success bg-success/10 border-success/30',
  pending: 'text-warning bg-warning/10 border-warning/30',
  failed: 'text-danger bg-danger/10 border-danger/30',
};

export default function PaymentStatusBadge({ status }: { status: Status }) {
  return (
    <span className={classNames('px-2.5 py-1 rounded-chip border text-xs capitalize', STYLES[status])}>
      {status}
    </span>
  );
}
