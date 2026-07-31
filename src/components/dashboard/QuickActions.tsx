import { useNavigate } from 'react-router-dom';
import { Rocket, Store, Wallet } from 'lucide-react';

const ACTIONS = [
  { label: 'Submit a Task', icon: Rocket, path: '/execute' },
  { label: 'Browse Marketplace', icon: Store, path: '/marketplace' },
  { label: 'View Payments', icon: Wallet, path: '/payments' },
];

export default function QuickActions() {
  const navigate = useNavigate();
  return (
    <div className="glass rounded-card p-5 flex flex-col gap-2">
      <h3 className="font-display text-ink mb-2">Quick Actions</h3>
      {ACTIONS.map((action) => (
        <button
          key={action.label}
          onClick={() => navigate(action.path)}
          className="flex items-center gap-3 px-3 py-2.5 rounded-card text-sm text-ink-muted hover:text-ink hover:bg-white/5 transition text-left"
        >
          <action.icon size={16} className="text-accent" />
          {action.label}
        </button>
      ))}
    </div>
  );
}
