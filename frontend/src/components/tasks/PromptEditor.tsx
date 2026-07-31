interface PromptEditorProps {
  value: string;
  onChange: (value: string) => void;
}

export default function PromptEditor({ value, onChange }: PromptEditorProps) {
  return (
    <div className="glass rounded-card p-1">
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        rows={4}
        placeholder="Build a startup pitch deck"
        className="w-full bg-transparent outline-none p-4 text-ink placeholder:text-ink-faint resize-none text-sm"
      />
    </div>
  );
}
