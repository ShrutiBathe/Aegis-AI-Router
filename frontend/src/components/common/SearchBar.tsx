import { Search } from 'lucide-react';

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}

export default function SearchBar({ value, onChange, placeholder = 'Search…' }: SearchBarProps) {
  return (
    <div className="glass rounded-chip flex items-center gap-2 px-4 py-2.5 w-full">
      <Search size={16} className="text-ink-faint" />
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="bg-transparent outline-none text-sm text-ink placeholder:text-ink-faint w-full"
      />
    </div>
  );
}
