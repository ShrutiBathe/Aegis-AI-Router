import { useState, ReactNode } from 'react';
import Navbar from './Navbar';
import Sidebar from './Sidebar';

export default function DashboardLayout({ children }: { children: ReactNode }) {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="min-h-screen bg-bg grid-overlay flex flex-col">
      <Navbar onMenuClick={() => setMobileOpen((v) => !v)} />
      <div className="flex flex-1 min-h-0">
        <Sidebar open={mobileOpen} />
        <main className="flex-1 p-4 md:p-8 overflow-y-auto">{children}</main>
      </div>
    </div>
  );
}
