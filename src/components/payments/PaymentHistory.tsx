import { usePayments } from '../../hooks/usePayments';
import TransactionTable from './TransactionTable';
import Loader from '../common/Loader';

export default function PaymentHistory() {
  const { payments, loading } = usePayments();
  if (loading) return <Loader label="Loading payments…" />;
  return <TransactionTable payments={payments} />;
}
