import { useState, FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import AuthLayout from '../components/layout/AuthLayout';
import { useAuth } from '../hooks/useAuth';
import { useNotifications } from '../contexts/NotificationContext';

export default function RegisterPage() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const { notify } = useNotifications();
  const navigate = useNavigate();

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      await register(name, { email, password });
      notify('Account created.', 'success');
      navigate('/dashboard');
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthLayout>
      <h1 className="font-display text-2xl text-ink mb-6">Create your account</h1>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div>
          <label className="text-xs text-ink-muted mb-1.5 block">Name</label>
          <input value={name} onChange={(e) => setName(e.target.value)} required className="w-full glass rounded-card px-4 py-2.5 text-sm text-ink outline-none" placeholder="Your name" />
        </div>
        <div>
          <label className="text-xs text-ink-muted mb-1.5 block">Email</label>
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required className="w-full glass rounded-card px-4 py-2.5 text-sm text-ink outline-none" placeholder="you@example.com" />
        </div>
        <div>
          <label className="text-xs text-ink-muted mb-1.5 block">Password</label>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required className="w-full glass rounded-card px-4 py-2.5 text-sm text-ink outline-none" placeholder="••••••••" />
        </div>
        <button type="submit" disabled={loading} className="w-full py-2.5 rounded-chip bg-grad-primary text-white text-sm font-medium disabled:opacity-50 hover:opacity-90 transition">
          {loading ? 'Creating account…' : 'Create Account'}
        </button>
      </form>
      <p className="text-sm text-ink-muted mt-6 text-center">
        Already have an account? <Link to="/login" className="text-primary hover:underline">Login</Link>
      </p>
    </AuthLayout>
  );
}
