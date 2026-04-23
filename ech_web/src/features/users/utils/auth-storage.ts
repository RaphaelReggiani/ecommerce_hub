import {
  clearStoredSession,
  getAccessToken,
  getRefreshToken,
  getStoredProfile,
  getStoredSession,
  getStoredUser,
  hasStoredSession,
  setStoredSession,
  updateStoredProfile,
  updateStoredUser,
  type AuthTokens,
} from "@/lib/auth/auth-session";
import type { SessionUser, UserProfile } from "@/types/common";

export const authStorage = {
  getSession: getStoredSession,
  getAccessToken,
  getRefreshToken,
  getUser: getStoredUser,
  getProfile: getStoredProfile,
  hasSession: hasStoredSession,

  setSession(
    tokens: AuthTokens,
    user?: SessionUser | null,
    profile?: UserProfile | null,
  ) {
    setStoredSession(tokens, user, profile);
  },

  clearSession() {
    clearStoredSession();
  },

  updateUser(user: SessionUser | null) {
    updateStoredUser(user);
  },

  updateProfile(profile: UserProfile | null) {
    updateStoredProfile(profile);
  },
};