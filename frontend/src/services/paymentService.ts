import { Payment } from '../types/payment';

export const MOCK_PAYMENTS: Payment[] = [
  { id: 'p1', taskName: 'Resume Analysis', agentName: 'Resume Agent', amount: 4, status: 'completed', algorandTxId: 'ALG7F2A9C...D31', date: new Date().toISOString(), stage: 'Payment' },
  { id: 'p2', taskName: 'Generate PPT', agentName: 'Presentation AI', amount: 7, status: 'completed', algorandTxId: 'ALG3B88E1...9AF', date: new Date(Date.now() - 3600000).toISOString(), stage: 'Payment' },
  { id: 'p3', taskName: 'Contract Review', agentName: 'Legal Draft Agent', amount: 8, status: 'failed', algorandTxId: 'ALG91DC4A...220', date: new Date(Date.now() - 7200000).toISOString(), stage: 'Payment' },
  { id: 'p4', taskName: 'Portfolio Rebalance', agentName: 'Portfolio AI', amount: 4, status: 'pending', algorandTxId: 'ALGE20A17...B0C', date: new Date(Date.now() - 9000000).toISOString(), stage: 'Payment' },
];

export async function getPayments(): Promise<Payment[]> {
  return MOCK_PAYMENTS;
}
