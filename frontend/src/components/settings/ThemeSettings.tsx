import { useTheme } from '../../contexts/ThemeContext';
import { classNames } from '../../utils/helpers';

export default function ThemeSettings() {
  const { theme, toggleTheme } = useTheme();
  return (
    <div className="glass rounded-card p-5">
      <h3 className="font-display text-ink mb-3">Theme</h3>
      <div className="flex gap-2">
        {(['dark', 'light'] as const).map((t) => (
          <button
            key={t}
            onClick={t !== theme ? toggleTheme : undefined}
            className={classNames(
              'px-4 py-2 rounded-card text-sm border capitalize transition',
              theme === t ? 'bg-grad-primary text-white border-transparent' : 'border-line text-ink-muted'
            )}
          >
            {t}
          </button>
        ))}
      </div>
    </div>
  );
}
