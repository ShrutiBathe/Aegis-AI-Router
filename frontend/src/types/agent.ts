export type AgentCategory =
  | 'Text' | 'Vision' | 'Finance' | 'Education' | 'Legal' | 'Medical' | 'Code' | 'Design';

export interface Agent {
  id: string;
  name: string;
  description: string;
  category: AgentCategory;
  price: number;
  rating: number;
  latencyMs: number;
  accuracy: number;
  owner: string;
  online: boolean;
  avatarColor: string;
}
