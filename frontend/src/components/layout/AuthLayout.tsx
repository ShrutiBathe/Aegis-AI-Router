import { ReactNode } from 'react';
import { Link } from 'react-router-dom';

export default function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-bg bg-grad-glow flex flex-col items-center justify-center px-4">
      <Link to="/" className="flex items-center gap-2 mb-8">
        <img src="/logo.svg" alt="Aegis Router" className="h-8 w-8" />
        <span className="font-display font-semibold text-lg text-ink">Aegis Router</span>
      </Link>
      <div className="glass rounded-card shadow-glass w-full max-w-md p-8">{children}</div>
    </div>
  );
}
