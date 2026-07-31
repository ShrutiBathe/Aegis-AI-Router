import ThemeSettings from '../components/settings/ThemeSettings';
import NotificationSettings from '../components/settings/NotificationSettings';
import PreferenceSettings from '../components/settings/PreferenceSettings';
import SecuritySettings from '../components/settings/SecuritySettings';

export default function SettingsPage() {
  return (
    <div className="max-w-3xl mx-auto flex flex-col gap-6">
      <h1 className="font-display text-2xl text-ink">Settings</h1>
      <ThemeSettings />
      <NotificationSettings />
      <PreferenceSettings />
      <SecuritySettings />
    </div>
  );
}
