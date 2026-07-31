import { useEffect, useMemo, useState } from 'react';
import { Task } from '../types/task';
import { getHistory } from '../services/historyService';
import HistoryFilters from '../components/history/HistoryFilters';
import HistoryTable from '../components/history/HistoryTable';
import Loader from '../components/common/Loader';

export default function HistoryPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    getHistory().then((data) => {
      setTasks(data);
      setLoading(false);
    });
  }, []);

  const filtered = useMemo(
    () => tasks.filter((t) => t.prompt.toLowerCase().includes(search.toLowerCase())),
    [tasks, search]
  );

  return (
    <div className="max-w-6xl mx-auto flex flex-col gap-6">
      <h1 className="font-display text-2xl text-ink">History</h1>
      <HistoryFilters search={search} onSearchChange={setSearch} />
      {loading ? <Loader label="Loading history…" /> : <HistoryTable tasks={filtered} />}
    </div>
  );
}
