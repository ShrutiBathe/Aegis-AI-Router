export type TaskStatus = 'queued' | 'running' | 'completed' | 'failed';

export interface Task {
  id: string;
  prompt: string;
  status: TaskStatus;
  selectedAgent: string;
  price: number;
  createdAt: string;
  executionTimeMs: number;
}

export type PipelineStage =
  | 'router' | 'planner' | 'registry' | 'ranking' | 'payment' | 'execution' | 'results';

export interface PipelineStageState {
  key: PipelineStage;
  label: string;
  status: 'pending' | 'running' | 'completed';
}
