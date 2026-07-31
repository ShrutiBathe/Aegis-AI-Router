import { useMemo, useState } from 'react';
import { useAgents } from '../hooks/useAgents';
import SearchBar from '../components/common/SearchBar';
import CategoryTabs from '../components/marketplace/CategoryTabs';
import AgentFilter from '../components/marketplace/AgentFilter';
import AgentGrid from '../components/marketplace/AgentGrid';
import Loader from '../components/common/Loader';

export default function MarketplacePage() {
  const { agents, loading } = useAgents();
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('All');
  const [sortBy, setSortBy] = useState('rating');

  const filtered = useMemo(() => {
    let result = agents.filter((a) => a.name.toLowerCase().includes(search.toLowerCase()));
    if (category !== 'All') result = result.filter((a) => a.category === category);
    result = [...result].sort((a, b) => {
      if (sortBy === 'price') return a.price - b.price;
      if (sortBy === 'latency') return a.latencyMs - b.latencyMs;
      return b.rating - a.rating;
    });
    return result;
  }, [agents, search, category, sortBy]);

  return (
    <div className="flex flex-col gap-6 max-w-7xl mx-auto">
      <div>
        <h1 className="font-display text-2xl text-ink mb-1">Marketplace</h1>
        <p className="text-sm text-ink-muted">Every agent the router can plan, rank, and pay on your behalf.</p>
      </div>

      <div className="flex flex-col md:flex-row gap-3 md:items-center md:justify-between">
        <div className="max-w-sm w-full">
          <SearchBar value={search} onChange={setSearch} placeholder="Search Agent…" />
        </div>
        <AgentFilter sortBy={sortBy} onSortChange={setSortBy} />
      </div>

      <CategoryTabs active={category} onChange={setCategory} />

      {loading ? <Loader label="Loading agents…" /> : <AgentGrid agents={filtered} />}
    </div>
  );
}
