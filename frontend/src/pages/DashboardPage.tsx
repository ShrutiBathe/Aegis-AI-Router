import { useAuth } from '../hooks/useAuth';
import StatsCards from '../components/dashboard/StatsCards';
import RecentTasks from '../components/dashboard/RecentTasks';
import ActiveAgents from '../components/dashboard/ActiveAgents';
import AnalyticsOverview from '../components/dashboard/AnalyticsOverview';
import QuickActions from '../components/dashboard/QuickActions';

export default function DashboardPage() {
  const { user } = useAuth();
  return (
    <div className="flex flex-col gap-6 max-w-7xl mx-auto">
      <h1 className="font-display text-2xl text-ink">Hello {user?.name ?? 'there'} 👋</h1>

      <StatsCards />

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 flex flex-col gap-6">
          <AnalyticsOverview />
          <div>
            <h2 className="font-display text-lg text-ink mb-3">Recent Tasks</h2>
            <RecentTasks />
          </div>
        </div>
        <div className="flex flex-col gap-6">
          <ActiveAgents />
          <QuickActions />
        </div>
      </div>
    </div>
  );
}
