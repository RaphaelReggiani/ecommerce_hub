import type { SessionUser, UserProfile } from "@/types/common";

const AUTH_STORAGE_KEY = "ech_auth_session";
const AUTH_COOKIE_NAME = "ech_auth";

export type AuthTokens = {
  access: string;
  refresh: string;
};

type StoredSession = {
  tokens: AuthTokens;
  user?: SessionUser | null;
  profile?: UserProfile | null;
};

function isBrowser(): boolean {
  return typeof window !== "undefined";
}

export function getStoredSession(): StoredSession | null {
  if (!isBrowser()) {
    return null;
  }

  const rawValue = window.localStorage.getItem(AUTH_STORAGE_KEY);

  if (!rawValue) {
    return null;
  }

  try {
    return JSON.parse(rawValue) as StoredSession;
  } catch {
    return null;
  }
}

export function setStoredSession(
  tokens: AuthTokens,
  user?: SessionUser | null,
  profile?: UserProfile | null,
): void {
  if (!isBrowser()) {
    return;
  }

  const payload: StoredSession = {
    tokens,
    user: user ?? null,
    profile: profile ?? null,
  };

  window.localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(payload));
  document.cookie = `${AUTH_COOKIE_NAME}=1; path=/`;
}

export function clearStoredSession(): void {
  if (!isBrowser()) {
    return;
  }

  window.localStorage.removeItem(AUTH_STORAGE_KEY);
  document.cookie = `${AUTH_COOKIE_NAME}=; path=/; Max-Age=0`;
}

export function getAccessToken(): string | null {
  return getStoredSession()?.tokens.access ?? null;
}

export function getRefreshToken(): string | null {
  return getStoredSession()?.tokens.refresh ?? null;
}

export function getStoredUser(): SessionUser | null {
  return getStoredSession()?.user ?? null;
}

export function getStoredProfile(): UserProfile | null {
  return getStoredSession()?.profile ?? null;
}

export function updateStoredUser(user: SessionUser | null): void {
  const session = getStoredSession();

  if (!session) {
    return;
  }

  setStoredSession(session.tokens, user, session.profile ?? null);
}

export function updateStoredProfile(profile: UserProfile | null): void {
  const session = getStoredSession();

  if (!session) {
    return;
  }

  setStoredSession(session.tokens, session.user ?? null, profile);
}

export function hasStoredSession(): boolean {
  const session = getStoredSession();
  return Boolean(session?.tokens.access && session?.tokens.refresh);
}

export function getAuthCookieName(): string {
  return AUTH_COOKIE_NAME;
}