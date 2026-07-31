interface AgentFilterProps {
  sortBy: string;
  onSortChange: (value: string) => void;
}

const OPTIONS = [
  { value: 'rating', label: 'Highest Rated' },
  { value: 'price', label: 'Lowest Price' },
  { value: 'latency', label: 'Fastest' },
];

export default function AgentFilter({ sortBy, onSortChange }: AgentFilterProps) {
  return (
    <select
      value={sortBy}
      onChange={(e) => onSortChange(e.target.value)}
      className="glass rounded-chip px-3 py-2 text-xs text-ink-muted outline-none"
    >
      {OPTIONS.map((opt) => (
        <option key={opt.value} value={opt.value} className="bg-bg-soft">
          {opt.label}
        </option>
      ))}
    </select>
  );
}
