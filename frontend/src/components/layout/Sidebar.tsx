import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard, Store, Rocket, BarChart3, History, Wallet, User, Settings,
} from 'lucide-react';
import { NAV_ITEMS } from '../../utils/constants';
import { classNames } from '../../utils/helpers';

const ICONS: Record<string, React.ComponentType<{ size?: number }>> = {
  LayoutDashboard, Store, Rocket, BarChart3, History, Wallet, User, Settings,
};

interface SidebarProps {
  open?: boolean;
}

export default function Sidebar({ open = true }: SidebarProps) {
  return (
    <aside
      className={classNames(
        'border-r border-line glass flex-col py-6 px-3 gap-1 w-60 shrink-0 h-full',
        open ? 'flex' : 'hidden md:flex'
      )}
    >
      {NAV_ITEMS.map((item) => {
        const Icon = ICONS[item.icon];
        return (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              classNames(
                'flex items-center gap-3 px-3 py-2.5 rounded-card text-sm transition-colors',
                isActive
                  ? 'bg-grad-primary text-white shadow-glow'
                  : 'text-ink-muted hover:text-ink hover:bg-white/5'
              )
            }
          >
            <Icon size={17} />
            {item.label}
          </NavLink>
        );
      })}
    </aside>
  );
}
