import { Routes, Route } from 'react-router-dom';
import PublicRoute from './PublicRoute';
import ProtectedRoute from './ProtectedRoute';

import LandingPage from '../pages/LandingPage';
import LoginPage from '../pages/LoginPage';
import RegisterPage from '../pages/RegisterPage';
import DashboardPage from '../pages/DashboardPage';
import MarketplacePage from '../pages/MarketplacePage';
import AgentDetailsPage from '../pages/AgentDetailsPage';
import TaskSubmissionPage from '../pages/TaskSubmissionPage';
import RouterExecutionPage from '../pages/RouterExecutionPage';
import AnalyticsPage from '../pages/AnalyticsPage';
import PaymentsPage from '../pages/PaymentsPage';
import HistoryPage from '../pages/HistoryPage';
import ProfilePage from '../pages/ProfilePage';
import SettingsPage from '../pages/SettingsPage';

export default function AppRoutes() {
  return (
    <Routes>
      <Route element={<PublicRoute />}>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
      </Route>

      <Route element={<ProtectedRoute />}>
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/marketplace" element={<MarketplacePage />} />
        <Route path="/marketplace/:agentId" element={<AgentDetailsPage />} />
        <Route path="/task-submission" element={<TaskSubmissionPage />} />
        <Route path="/execute" element={<RouterExecutionPage />} />
        <Route path="/analytics" element={<AnalyticsPage />} />
        <Route path="/payments" element={<PaymentsPage />} />
        <Route path="/history" element={<HistoryPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Route>
    </Routes>
  );
}
