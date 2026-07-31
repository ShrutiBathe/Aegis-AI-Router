import { Link, useNavigate } from 'react-router-dom';
import { Menu } from 'lucide-react';
import PipelineFlow from '../router/PipelineFlow';
import ThemeToggle from '../common/ThemeToggle';
import NotificationBell from '../common/NotificationBell';
import UserAvatar from '../common/UserAvatar';
import { useAuth } from '../../hooks/useAuth';

interface NavbarProps {
  onMenuClick?: () => void;
}

export default function Navbar({ onMenuClick }: NavbarProps) {
  const navigate = useNavigate();
  const { user } = useAuth();

  return (
    <header className="sticky top-0 z-30 border-b border-line glass px-4 md:px-6 py-3 flex items-center justify-between gap-4">
      <div className="flex items-center gap-3">
        {onMenuClick && (
          <button onClick={onMenuClick} className="md:hidden text-ink-muted">
            <Menu size={20} />
          </button>
        )}
        <Link to="/" className="flex items-center gap-2">
          <img src="/logo.svg" alt="Aegis Router" className="h-7 w-7" />
          <span className="font-display font-semibold text-ink hidden sm:inline">Aegis Router</span>
        </Link>
      </div>

      {/* Persistent mini pipeline — always visible reminder that the router is the product */}
      <div className="hidden lg:block">
        <PipelineFlow mode="mini" />
      </div>

      <div className="flex items-center gap-3">
        <ThemeToggle />
        <NotificationBell />
        {user ? (
          <button onClick={() => navigate('/profile')}>
            <UserAvatar initials={user.avatarInitials} />
          </button>
        ) : (
          <button
            onClick={() => navigate('/login')}
            className="px-4 py-2 rounded-chip bg-grad-primary text-white text-sm font-medium"
          >
            Login
          </button>
        )}
      </div>
    </header>
  );
}
