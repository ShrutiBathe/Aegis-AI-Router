import { createContext, useContext, useState, ReactNode } from 'react';
import { UserProfile } from '../types/user';
import * as authService from '../services/authService';
import { Credentials } from '../types/auth';

interface AuthContextValue {
  user: UserProfile | null;
  isAuthenticated: boolean;
  login: (creds: Credentials) => Promise<void>;
  register: (name: string, creds: Credentials) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null);

  async function login(creds: Credentials) {
    const profile = await authService.login(creds);
    setUser(profile);
  }

  async function register(name: string, creds: Credentials) {
    const profile = await authService.register(name, creds);
    setUser(profile);
  }

  function logout() {
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuthContext() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuthContext must be used within AuthProvider');
  return ctx;
}
