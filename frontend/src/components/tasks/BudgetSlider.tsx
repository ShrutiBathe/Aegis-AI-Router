import { formatCurrency } from '../../utils/formatters';

interface BudgetSliderProps {
  value: number;
  onChange: (value: number) => void;
}

export default function BudgetSlider({ value, onChange }: BudgetSliderProps) {
  return (
    <div>
      <div className="flex justify-between text-sm mb-2">
        <span className="text-ink-muted">Budget</span>
        <span className="text-ink font-display">{formatCurrency(value)}</span>
      </div>
      <input
        type="range"
        min={1}
        max={50}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full accent-primary"
      />
    </div>
  );
}
