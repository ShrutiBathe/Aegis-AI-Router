interface LocalAIToggleProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
}

export default function LocalAIToggle({ checked, onChange }: LocalAIToggleProps) {
  return (
    <label className="flex items-center justify-between text-sm text-ink-muted cursor-pointer">
      <span>Use Local AI</span>
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        className="h-4 w-4 accent-primary"
      />
    </label>
  );
}
