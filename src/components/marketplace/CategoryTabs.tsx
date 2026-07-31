import { AGENT_CATEGORIES } from '../../utils/constants';
import { classNames } from '../../utils/helpers';

interface CategoryTabsProps {
  active: string;
  onChange: (value: string) => void;
}

export default function CategoryTabs({ active, onChange }: CategoryTabsProps) {
  return (
    <div className="flex flex-wrap gap-2">
      {AGENT_CATEGORIES.map((cat) => (
        <button
          key={cat}
          onClick={() => onChange(cat)}
          className={classNames(
            'px-4 py-1.5 rounded-chip text-xs font-medium border transition',
            active === cat
              ? 'bg-grad-primary text-white border-transparent'
              : 'border-line text-ink-muted hover:text-ink hover:border-primary/40'
          )}
        >
          {cat}
        </button>
      ))}
    </div>
  );
}
