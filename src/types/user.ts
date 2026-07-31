export interface UserProfile {
  id: string;
  name: string;
  email: string;
  wallet: number;
  apiKey: string;
  subscription: 'Free' | 'Pro' | 'Team';
  avatarInitials: string;
}
