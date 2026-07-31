export interface DailyPoint {
  label: string;
  tasks: number;
  revenue: number;
  latency: number;
  successRate: number;
}

export interface AgentUsage {
  agent: string;
  usage: number;
}
