import { Bell } from 'lucide-react';
import { useNotifications } from '../../contexts/NotificationContext';

export default function NotificationBell() {
  const { notifications } = useNotifications();
  return (
    <button aria-label="Notifications" className="relative h-9 w-9 rounded-full glass flex items-center justify-center text-ink-muted hover:text-ink transition">
      <Bell size={16} />
      {notifications.length > 0 && (
        <span className="absolute -top-1 -right-1 h-4 w-4 rounded-full bg-danger text-[10px] flex items-center justify-center text-white">
          {notifications.length}
        </span>
      )}
    </button>
  );
}
