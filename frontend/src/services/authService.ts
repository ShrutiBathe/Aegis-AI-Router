import { Credentials } from '../types/auth';
import { UserProfile } from '../types/user';
import { sleep } from '../utils/helpers';

// Mock auth service — replace with real calls to the Aegis Router backend.
export async function login(creds: Credentials): Promise<UserProfile> {
  await sleep(500);
  if (!creds.email || !creds.password) throw new Error('Email and password are required.');
  return {
    id: 'user_1',
    name: 'Shruti',
    email: creds.email,
    wallet: 1200,
    apiKey: 'ar_live_9f2a...c31d',
    subscription: 'Pro',
    avatarInitials: 'S',
  };
}

export async function register(name: string, creds: Credentials): Promise<UserProfile> {
  await sleep(500);
  return {
    id: 'user_1',
    name,
    email: creds.email,
    wallet: 0,
    apiKey: 'ar_live_9f2a...c31d',
    subscription: 'Free',
    avatarInitials: name.slice(0, 1).toUpperCase(),
  };
}
