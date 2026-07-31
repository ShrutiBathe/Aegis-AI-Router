import { Task } from '../types/task';
import { MOCK_TASKS } from './taskService';

export async function getHistory(): Promise<Task[]> {
  return MOCK_TASKS;
}
