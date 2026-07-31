export const APP_NAME = 'Aegis Router';

export const NAV_ITEMS = [
  { label: 'Dashboard', path: '/dashboard', icon: 'LayoutDashboard' },
  { label: 'Marketplace', path: '/marketplace', icon: 'Store' },
  { label: 'Execute', path: '/execute', icon: 'Rocket' },
  { label: 'Analytics', path: '/analytics', icon: 'BarChart3' },
  { label: 'History', path: '/history', icon: 'History' },
  { label: 'Payments', path: '/payments', icon: 'Wallet' },
  { label: 'Profile', path: '/profile', icon: 'User' },
  { label: 'Settings', path: '/settings', icon: 'Settings' },
] as const;

export const AGENT_CATEGORIES = [
  'All', 'Text', 'Vision', 'Finance', 'Education', 'Legal', 'Medical', 'Code', 'Design',
] as const;

export const PIPELINE_STAGES = [
  { key: 'router', label: 'Router' },
  { key: 'planner', label: 'Planner' },
  { key: 'registry', label: 'Registry' },
  { key: 'ranking', label: 'Ranking' },
  { key: 'payment', label: 'Payment' },
  { key: 'execution', label: 'Execution' },
  { key: 'results', label: 'Results' },
] as const;
