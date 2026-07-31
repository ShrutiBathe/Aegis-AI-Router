import { DailyPoint, AgentUsage } from '../types/analytics';

export const MOCK_DAILY: DailyPoint[] = [
  { label: 'Mon', tasks: 52, revenue: 2100, latency: 980, successRate: 97.2 },
  { label: 'Tue', tasks: 61, revenue: 2600, latency: 1020, successRate: 98.1 },
  { label: 'Wed', tasks: 48, revenue: 1900, latency: 890, successRate: 96.4 },
  { label: 'Thu', tasks: 73, revenue: 3100, latency: 1150, successRate: 98.9 },
  { label: 'Fri', tasks: 68, revenue: 2900, latency: 1005, successRate: 97.6 },
  { label: 'Sat', tasks: 40, revenue: 1600, latency: 870, successRate: 98.4 },
  { label: 'Sun', tasks: 44, revenue: 1800, latency: 910, successRate: 99.0 },
];

export const MOCK_AGENT_USAGE: AgentUsage[] = [
  { agent: 'Resume Agent', usage: 128 },
  { agent: 'Presentation AI', usage: 96 },
  { agent: 'Image Generator', usage: 84 },
  { agent: 'Legal Draft Agent', usage: 51 },
  { agent: 'Portfolio AI', usage: 44 },
];

export async function getDailyAnalytics(): Promise<DailyPoint[]> {
  return MOCK_DAILY;
}

export async function getAgentUsage(): Promise<AgentUsage[]> {
  return MOCK_AGENT_USAGE;
}
