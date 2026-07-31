import SearchBar from '../common/SearchBar';

interface HistoryFiltersProps {
  search: string;
  onSearchChange: (v: string) => void;
}

export default function HistoryFilters({ search, onSearchChange }: HistoryFiltersProps) {
  return (
    <div className="max-w-sm">
      <SearchBar value={search} onChange={onSearchChange} placeholder="Search history…" />
    </div>
  );
}
