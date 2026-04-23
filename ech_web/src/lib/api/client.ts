import { env } from "@/config/env";
import {
  clearStoredSession,
  getAccessToken,
  getRefreshToken,
  getStoredProfile,
  getStoredUser,
  setStoredSession,
  type AuthTokens,
} from "@/lib/auth/auth-session";
import { ApiClientError, parseApiError } from "@/lib/api/error-handler";

type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

type RequestOptions = {
  method?: HttpMethod;
  body?: unknown;
  headers?: HeadersInit;
  auth?: boolean;
  signal?: AbortSignal;
  accessToken?: string;
  retryOnAuthError?: boolean;
};

type RefreshTokenResponse = {
  access: string;
  refresh?: string;
};

function buildHeaders(body: unknown, headers?: HeadersInit): Headers {
  const finalHeaders = new Headers(headers);

  if (!(body instanceof FormData) && !finalHeaders.has("Content-Type")) {
    finalHeaders.set("Content-Type", "application/json");
  }

  return finalHeaders;
}

async function refreshAccessToken(): Promise<string | null> {
  const refresh = getRefreshToken();

  if (!refresh) {
    clearStoredSession();
    return null;
  }

  try {
    const response = await fetch(`${env.API_BASE_URL}/users/refresh-token/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ refresh }),
    });

    if (!response.ok) {
      clearStoredSession();
      return null;
    }

    const data = (await response.json()) as RefreshTokenResponse;

    const nextTokens: AuthTokens = {
      access: data.access,
      refresh: data.refresh ?? refresh,
    };

    setStoredSession(nextTokens, getStoredUser(), getStoredProfile());
    return nextTokens.access;
  } catch {
    clearStoredSession();
    return null;
  }
}

async function request<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const {
    method = "GET",
    body,
    headers,
    auth = false,
    signal,
    accessToken,
    retryOnAuthError = true,
  } = options;

  const finalHeaders = buildHeaders(body, headers);
  const resolvedAccessToken = accessToken ?? (auth ? getAccessToken() : null);

  if (resolvedAccessToken) {
    finalHeaders.set("Authorization", `Bearer ${resolvedAccessToken}`);
  }

  const response = await fetch(`${env.API_BASE_URL}${path}`, {
    method,
    headers: finalHeaders,
    body:
      body === undefined
        ? undefined
        : body instanceof FormData
          ? body
          : JSON.stringify(body),
    signal,
  });

  if (!response.ok) {
    const error = await parseApiError(response);

    if (error.status === 401 && auth && retryOnAuthError && !accessToken) {
      const nextAccessToken = await refreshAccessToken();

      if (nextAccessToken) {
        return request<T>(path, {
          ...options,
          accessToken: nextAccessToken,
          retryOnAuthError: false,
        });
      }

      clearStoredSession();
    }

    throw error;
  }

  if (response.status === 204 || response.status === 205) {
    return undefined as T;
  }

  try {
    return (await response.json()) as T;
  } catch {
    throw new ApiClientError("Invalid JSON response.", response.status);
  }
}

export const apiClient = {
  get<T>(path: string, options?: Omit<RequestOptions, "method" | "body">) {
    return request<T>(path, { ...options, method: "GET" });
  },

  post<T>(
    path: string,
    body?: unknown,
    options?: Omit<RequestOptions, "method" | "body">,
  ) {
    return request<T>(path, { ...options, method: "POST", body });
  },

  put<T>(
    path: string,
    body?: unknown,
    options?: Omit<RequestOptions, "method" | "body">,
  ) {
    return request<T>(path, { ...options, method: "PUT", body });
  },

  patch<T>(
    path: string,
    body?: unknown,
    options?: Omit<RequestOptions, "method" | "body">,
  ) {
    return request<T>(path, { ...options, method: "PATCH", body });
  },

  delete<T>(path: string, options?: Omit<RequestOptions, "method" | "body">) {
    return request<T>(path, { ...options, method: "DELETE" });
  },
};