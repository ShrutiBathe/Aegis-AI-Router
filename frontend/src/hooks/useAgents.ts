import { useEffect, useState } from 'react';
import { Agent } from '../types/agent';
import { getAgents } from '../services/agentService';

export function useAgents() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAgents().then((data) => {
      setAgents(data);
      setLoading(false);
    });
  }, []);

  return { agents, loading };
}
