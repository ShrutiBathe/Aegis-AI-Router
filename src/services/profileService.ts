import { UserProfile } from '../types/user';

export async function updateProfile(profile: Partial<UserProfile>): Promise<UserProfile> {
  return { ...profile } as UserProfile;
}
