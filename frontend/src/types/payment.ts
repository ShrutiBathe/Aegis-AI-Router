export type PaymentStatus = 'pending' | 'completed' | 'failed';

export interface Payment {
  id: string;
  taskName: string;
  agentName: string;
  amount: number;
  status: PaymentStatus;
  algorandTxId: string;
  date: string;
  stage: 'Payment';
}
