import { useAuth } from '../hooks/useAuth';
import ProfileCard from '../components/profile/ProfileCard';
import WalletSection from '../components/profile/WalletSection';
import APIKeySection from '../components/profile/APIKeySection';
import ErrorPage from '../components/common/ErrorPage';

export default function ProfilePage() {
  const { user } = useAuth();
  if (!user) return <ErrorPage title="No profile loaded" message="Log in to view your profile." />;

  return (
    <div className="max-w-3xl mx-auto flex flex-col gap-6">
      <h1 className="font-display text-2xl text-ink">Profile</h1>
      <ProfileCard user={user} />
      <div className="grid md:grid-cols-2 gap-4">
        <WalletSection balance={user.wallet} />
        <div className="glass rounded-card p-5">
          <p className="text-sm text-ink-muted mb-1">Subscription</p>
          <p className="font-display text-2xl text-ink">{user.subscription}</p>
        </div>
      </div>
      <APIKeySection apiKey={user.apiKey} />
    </div>
  );
}
