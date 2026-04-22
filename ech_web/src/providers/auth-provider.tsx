"use client";

import {
  createContext,
  ReactNode,
  useContext,
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

type InitialAuthState = {
  user: SessionUser | null;
  profile: UserProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
};

function getInitialAuthState(): InitialAuthState {
  return {
    user: getStoredUser(),
    profile: getStoredProfile(),
    isAuthenticated: hasStoredSession(),
    isLoading: false,
  };
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [state, setState] = useState<InitialAuthState>(() => getInitialAuthState());

  function setSession(
    tokens: AuthTokens,
    nextUser?: SessionUser | null,
    nextProfile?: UserProfile | null,
  ): void {
    setStoredSession(tokens, nextUser ?? null, nextProfile ?? null);

    setState({
      user: nextUser ?? null,
      profile: nextProfile ?? null,
      isAuthenticated: true,
      isLoading: false,
    });
  }

  function logout(): void {
    clearStoredSession();

    setState({
      user: null,
      profile: null,
      isAuthenticated: false,
      isLoading: false,
    });
  }

  function refreshUser(nextUser: SessionUser | null): void {
    updateStoredUser(nextUser);

    setState((current) => ({
      ...current,
      user: nextUser,
    }));
  }

  function refreshProfile(nextProfile: UserProfile | null): void {
    updateStoredProfile(nextProfile);

    setState((current) => ({
      ...current,
      profile: nextProfile,
    }));
  }

  const value = useMemo<AuthContextValue>(
    () => ({
      user: state.user,
      profile: state.profile,
      isAuthenticated: state.isAuthenticated,
      isLoading: state.isLoading,
      setSession,
      logout,
      refreshUser,
      refreshProfile,
    }),
    [state],
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