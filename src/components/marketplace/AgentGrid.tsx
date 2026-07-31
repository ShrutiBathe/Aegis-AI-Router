import { Agent } from '../../types/agent';
import AgentCard from './AgentCard';
import EmptyState from '../common/EmptyState';

export default function AgentGrid({ agents }: { agents: Agent[] }) {
  if (agents.length === 0) {
    return <EmptyState title="No agents match" description="Try a different category or search term." />;
  }
  return (
    <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {agents.map((agent) => (
        <AgentCard key={agent.id} agent={agent} />
      ))}
    </div>
  );
}
