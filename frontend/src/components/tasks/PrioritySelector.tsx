import { classNames } from '../../utils/helpers';

const OPTIONS = ['Fastest', 'Balanced', 'High Quality'];

interface PrioritySelectorProps {
  value: string;
  onChange: (value: string) => void;
}

export default function PrioritySelector({ value, onChange }: PrioritySelectorProps) {
  return (
    <div>
      <p className="text-sm text-ink-muted mb-2">Preferred Speed / Priority</p>
      <div className="flex gap-2">
        {OPTIONS.map((opt) => (
          <button
            key={opt}
            onClick={() => onChange(opt)}
            className={classNames(
              'flex-1 px-3 py-2 rounded-card text-xs border transition',
              value === opt
                ? 'bg-grad-primary text-white border-transparent'
                : 'border-line text-ink-muted hover:text-ink'
            )}
          >
            {opt}
          </button>
        ))}
      </div>
    </div>
  );
}
