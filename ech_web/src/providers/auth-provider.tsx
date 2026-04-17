"use client";

import {
  createContext,
  ReactNode,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  clearStoredSession,
  getStoredProfile,
  getStoredUser,
  hasStoredSession,
  setStoredSession,
  updateStoredProfile,
  updateStoredUser,
  type AuthTokens,
} from "@/lib/auth/auth-session";
import type { SessionUser, UserProfile } from "@/types/common";

type AuthContextValue = {
  user: SessionUser | null;
  profile: UserProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  setSession: (
    tokens: AuthTokens,
    user?: SessionUser | null,
    profile?: UserProfile | null,
  ) => void;
  logout: () => void;
  refreshUser: (user: SessionUser | null) => void;
  refreshProfile: (profile: UserProfile | null) => void;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

type AuthProviderProps = {
  children: ReactNode;
};

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<SessionUser | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const storedUser = getStoredUser();
    const storedProfile = getStoredProfile();
    const authenticated = hasStoredSession();

    setUser(storedUser);
    setProfile(storedProfile);
    setIsAuthenticated(authenticated);
    setIsLoading(false);
  }, []);

  function setSession(
    tokens: AuthTokens,
    nextUser?: SessionUser | null,
    nextProfile?: UserProfile | null,
  ): void {
    setStoredSession(tokens, nextUser ?? null, nextProfile ?? null);
    setUser(nextUser ?? null);
    setProfile(nextProfile ?? null);
    setIsAuthenticated(true);
  }

  function logout(): void {
    clearStoredSession();
    setUser(null);
    setProfile(null);
    setIsAuthenticated(false);
  }

  function refreshUser(nextUser: SessionUser | null): void {
    updateStoredUser(nextUser);
    setUser(nextUser);
  }

  function refreshProfile(nextProfile: UserProfile | null): void {
    updateStoredProfile(nextProfile);
    setProfile(nextProfile);
  }

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      profile,
      isAuthenticated,
      isLoading,
      setSession,
      logout,
      refreshUser,
      refreshProfile,
    }),
    [user, profile, isAuthenticated, isLoading],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used within AuthProvider.");
  }

  return context;
}