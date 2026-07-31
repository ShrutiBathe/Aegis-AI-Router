import { useEffect, useState } from 'react';
import { DailyPoint, AgentUsage } from '../types/analytics';
import { getDailyAnalytics, getAgentUsage } from '../services/analyticsService';

export function useAnalytics() {
  const [daily, setDaily] = useState<DailyPoint[]>([]);
  const [usage, setUsage] = useState<AgentUsage[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getDailyAnalytics(), getAgentUsage()]).then(([d, u]) => {
      setDaily(d);
      setUsage(u);
      setLoading(false);
    });
  }, []);

  return { daily, usage, loading };
}
