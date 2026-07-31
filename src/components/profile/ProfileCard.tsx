import { UserProfile } from '../../types/user';
import UserAvatar from '../common/UserAvatar';

export default function ProfileCard({ user }: { user: UserProfile }) {
  return (
    <div className="glass rounded-card p-6 flex items-center gap-4">
      <UserAvatar initials={user.avatarInitials} size={56} />
      <div>
        <p className="font-display text-lg text-ink">{user.name}</p>
        <p className="text-sm text-ink-muted">{user.email}</p>
        <span className="mt-1 inline-block px-2.5 py-0.5 rounded-chip bg-secondary/10 border border-secondary/30 text-secondary text-xs">
          {user.subscription}
        </span>
      </div>
    </div>
  );
}
