import { Task } from '../types/task';

export const MOCK_TASKS: Task[] = [
  { id: 't1', prompt: 'Generate PPT', status: 'completed', selectedAgent: 'Presentation AI', price: 6, createdAt: new Date(Date.now() - 2 * 60000).toISOString(), executionTimeMs: 118000 },
  { id: 't2', prompt: 'Resume Analysis', status: 'running', selectedAgent: 'Resume Agent', price: 3, createdAt: new Date().toISOString(), executionTimeMs: 0 },
  { id: 't3', prompt: 'Portfolio Rebalance', status: 'completed', selectedAgent: 'Portfolio AI', price: 4, createdAt: new Date(Date.now() - 3600000).toISOString(), executionTimeMs: 54000 },
  { id: 't4', prompt: 'Contract Review', status: 'failed', selectedAgent: 'Legal Draft Agent', price: 8, createdAt: new Date(Date.now() - 7200000).toISOString(), executionTimeMs: 12000 },
];

export async function getRecentTasks(): Promise<Task[]> {
  return MOCK_TASKS;
}

export async function submitTask(_prompt: string): Promise<{ taskId: string }> {
  return { taskId: `t_${Date.now()}` };
}
