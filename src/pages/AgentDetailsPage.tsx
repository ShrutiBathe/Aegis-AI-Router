import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { Agent } from '../types/agent';
import { getAgentById } from '../services/agentService';
import { formatCurrency, formatLatency, formatPercent } from '../utils/formatters';
import RatingBadge from '../components/marketplace/RatingBadge';
import Loader from '../components/common/Loader';
import ErrorPage from '../components/common/ErrorPage';

const COST_HISTORY = [
  { day: 'Mon', cost: 3.2 }, { day: 'Tue', cost: 3.0 }, { day: 'Wed', cost: 3.4 },
  { day: 'Thu', cost: 2.9 }, { day: 'Fri', cost: 3.1 }, { day: 'Sat', cost: 3.3 }, { day: 'Sun', cost: 3.0 },
];

export default function AgentDetailsPage() {
  const { agentId } = useParams();
  const navigate = useNavigate();
  const [agent, setAgent] = useState<Agent | null | undefined>(undefined);

  useEffect(() => {
    if (agentId) getAgentById(agentId).then(setAgent);
  }, [agentId]);

  if (agent === undefined) return <Loader label="Loading agent…" />;
  if (!agent) return <ErrorPage title="Agent not found" message="This agent may have been removed from the registry." />;

  return (
    <div className="max-w-5xl mx-auto flex flex-col gap-6">
      <div className="glass rounded-card p-6 flex flex-col md:flex-row md:items-center gap-4 justify-between">
        <div className="flex items-center gap-4">
          <div className="h-14 w-14 rounded-card flex items-center justify-center font-display text-white text-xl" style={{ background: agent.avatarColor }}>
            {agent.name.slice(0, 1)}
          </div>
          <div>
            <h1 className="font-display text-xl text-ink">{agent.name}</h1>
            <p className="text-sm text-ink-faint">{agent.owner} · {agent.category}</p>
          </div>
        </div>
        <button
          onClick={() => navigate('/task-submission', { state: { preferredAgent: agent.name } })}
          className="px-5 py-2.5 rounded-chip bg-grad-primary text-white text-sm font-medium hover:opacity-90 transition"
        >
          Try Agent
        </button>
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        <div className="glass rounded-card p-5"><p className="text-xs text-ink-faint mb-1">Price</p><p className="font-display text-ink">{formatCurrency(agent.price)}</p></div>
        <div className="glass rounded-card p-5"><p className="text-xs text-ink-faint mb-1">Rating</p><RatingBadge rating={agent.rating} /></div>
        <div className="glass rounded-card p-5"><p className="text-xs text-ink-faint mb-1">Latency</p><p className="font-display text-ink">{formatLatency(agent.latencyMs)}</p></div>
      </div>

      <div className="glass rounded-card p-6">
        <h2 className="font-display text-ink mb-2">Overview</h2>
        <p className="text-sm text-ink-muted">{agent.description}</p>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <div className="glass rounded-card p-6">
          <h2 className="font-display text-ink mb-3">Capabilities</h2>
          <ul className="text-sm text-ink-muted flex flex-col gap-1.5 list-disc list-inside">
            <li>Supports {agent.category} tasks</li>
            <li>{formatPercent(agent.accuracy)} historical accuracy</li>
            <li>Callable via router API and direct agent API</li>
          </ul>
        </div>
        <div className="glass rounded-card p-6">
          <h2 className="font-display text-ink mb-3">Performance — Cost History</h2>
          <ResponsiveContainer width="100%" height={140}>
            <LineChart data={COST_HISTORY}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.08)" />
              <XAxis dataKey="day" stroke="#64748B" fontSize={11} />
              <YAxis stroke="#64748B" fontSize={11} />
              <Tooltip contentStyle={{ background: '#141F38', border: '1px solid rgba(148,163,184,0.2)', borderRadius: 12 }} />
              <Line type="monotone" dataKey="cost" stroke="#3B82F6" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="glass rounded-card p-6">
        <h2 className="font-display text-ink mb-2">Health & Wallet</h2>
        <p className="text-sm text-ink-muted">
          {agent.online ? 'Online and accepting tasks.' : 'Currently offline.'} Payments settle to the agent owner's wallet via x402 on task completion.
        </p>
      </div>
    </div>
  );
}
