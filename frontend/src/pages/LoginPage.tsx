import { useState, FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import AuthLayout from '../components/layout/AuthLayout';
import { useAuth } from '../hooks/useAuth';
import { useNotifications } from '../contexts/NotificationContext';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();
  const { notify } = useNotifications();
  const navigate = useNavigate();

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login({ email, password });
      notify('Welcome back.', 'success');
      navigate('/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthLayout>
      <h1 className="font-display text-2xl text-ink mb-6">Welcome Back</h1>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div>
          <label className="text-xs text-ink-muted mb-1.5 block">Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full glass rounded-card px-4 py-2.5 text-sm text-ink outline-none"
            placeholder="you@example.com"
          />
        </div>
        <div>
          <label className="text-xs text-ink-muted mb-1.5 block">Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="w-full glass rounded-card px-4 py-2.5 text-sm text-ink outline-none"
            placeholder="••••••••"
          />
        </div>
        {error && <p className="text-xs text-danger">{error}</p>}
        <button
          type="submit"
          disabled={loading}
          className="w-full py-2.5 rounded-chip bg-grad-primary text-white text-sm font-medium disabled:opacity-50 hover:opacity-90 transition"
        >
          {loading ? 'Logging in…' : 'Login'}
        </button>
      </form>
      <p className="text-sm text-ink-muted mt-6 text-center">
        Don't have an account? <Link to="/register" className="text-primary hover:underline">Register</Link>
      </p>
    </AuthLayout>
  );
}
