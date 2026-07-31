import { useEffect, useState } from 'react';
import { Payment } from '../types/payment';
import { getPayments } from '../services/paymentService';

export function usePayments() {
  const [payments, setPayments] = useState<Payment[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getPayments().then((data) => {
      setPayments(data);
      setLoading(false);
    });
  }, []);

  return { payments, loading };
}
