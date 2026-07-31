import { Agent } from '../types/agent';

export const MOCK_AGENTS: Agent[] = [
  { id: 'a1', name: 'Resume Agent', description: 'Parses and rewrites resumes for target roles.', category: 'Text', price: 3, rating: 4.9, latencyMs: 820, accuracy: 98, owner: 'Nova Labs', online: true, avatarColor: '#3B82F6' },
  { id: 'a2', name: 'Image Generator', description: 'Generates and edits images from prompts.', category: 'Vision', price: 5, rating: 4.8, latencyMs: 1400, accuracy: 95, owner: 'Pixel Foundry', online: true, avatarColor: '#8B5CF6' },
  { id: 'a3', name: 'Presentation AI', description: 'Builds full slide decks from a brief.', category: 'Design', price: 6, rating: 4.7, latencyMs: 2100, accuracy: 97, owner: 'DeckWorks', online: true, avatarColor: '#22D3EE' },
  { id: 'a4', name: 'Legal Draft Agent', description: 'Drafts and reviews standard legal contracts.', category: 'Legal', price: 8, rating: 4.7, latencyMs: 1900, accuracy: 96, owner: 'Statute AI', online: true, avatarColor: '#F59E0B' },
  { id: 'a5', name: 'Portfolio AI', description: 'Builds and analyzes investment portfolios.', category: 'Finance', price: 4, rating: 4.6, latencyMs: 950, accuracy: 94, owner: 'Ledger Labs', online: false, avatarColor: '#22C55E' },
  { id: 'a6', name: 'Code Reviewer', description: 'Reviews pull requests and suggests fixes.', category: 'Code', price: 5, rating: 4.8, latencyMs: 1100, accuracy: 97, owner: 'Compilr', online: true, avatarColor: '#3B82F6' },
  { id: 'a7', name: 'Med Notes Agent', description: 'Summarizes clinical notes into structured records.', category: 'Medical', price: 9, rating: 4.5, latencyMs: 1700, accuracy: 93, owner: 'Clarity Health', online: true, avatarColor: '#EF4444' },
  { id: 'a8', name: 'Tutor Agent', description: 'Personalized step-by-step tutoring on any subject.', category: 'Education', price: 2, rating: 4.9, latencyMs: 700, accuracy: 98, owner: 'Learnly', online: true, avatarColor: '#8B5CF6' },
];

export async function getAgents(): Promise<Agent[]> {
  return MOCK_AGENTS;
}

export async function getAgentById(id: string): Promise<Agent | undefined> {
  return MOCK_AGENTS.find((a) => a.id === id);
}
