import { apiClient } from "@/lib/api/client";
import { clearStoredSession, getRefreshToken, setStoredSession, type AuthTokens } from "@/lib/auth/auth-session";

type RefreshTokenResponse = {
  access: string;
  refresh?: string;
};

type RequestConfig = {
  headers?: Record<string, string>;
  auth?: boolean;
  accessToken?: string;
  _retry?: boolean;
};

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function getErrorStatus(error: unknown): number | null {
  if (!isObject(error)) return null;

  const status = error.status;
  if (typeof status === "number") return status;

  const response = error.response;
  if (isObject(response) && typeof response.status === "number") {
    return response.status;
  }

  return null;
}

async function refreshAccessToken(): Promise<AuthTokens | null> {
  const refresh = getRefreshToken();

  if (!refresh) {
    clearStoredSession();
    return null;
  }

  try {
    const response = await apiClient.post<RefreshTokenResponse>(
      "/users/refresh-token/",
      { refresh },
      {
        auth: false,
      },
    );

    const nextTokens: AuthTokens = {
      access: response.access,
      refresh: response.refresh ?? refresh,
    };

    setStoredSession(nextTokens);
    return nextTokens;
  } catch {
    clearStoredSession();
    return null;
  }
}

export function withAuthHeaders(config: RequestConfig = {}): RequestConfig {
  const headers = { ...(config.headers ?? {}) };

  if (config.accessToken) {
    headers.Authorization = `Bearer ${config.accessToken}`;
    return {
      ...config,
      headers,
    };
  }

  return {
    ...config,
    headers,
  };
}

export async function handleAuthRetry<T>(
  request: (config?: RequestConfig) => Promise<T>,
  config: RequestConfig = {},
  error: unknown,
): Promise<T> {
  const status = getErrorStatus(error);

  if (status !== 401 || config._retry) {
    throw error;
  }

  const nextTokens = await refreshAccessToken();

  if (!nextTokens) {
    throw error;
  }

  return request({
    ...config,
    _retry: true,
    accessToken: nextTokens.access,
  });
}