import type { ApiErrorResponse } from "@/types/api";

export class ApiClientError extends Error {
  status: number;
  data: ApiErrorResponse | null;

  constructor(
    message: string,
    status: number,
    data: ApiErrorResponse | null = null,
  ) {
    super(message);
    this.name = "ApiClientError";
    this.status = status;
    this.data = data;
  }
}

function extractErrorMessage(data: ApiErrorResponse | null): string | null {
  if (!data) {
    return null;
  }

  if (typeof data.detail === "string" && data.detail.trim()) {
    return data.detail;
  }

  if (typeof data.message === "string" && data.message.trim()) {
    return data.message;
  }

  const entries = Object.entries(data).filter(
    ([key]) => !["detail", "message", "status", "errors"].includes(key),
  );

  for (const [, value] of entries) {
    if (Array.isArray(value) && value.length > 0 && typeof value[0] === "string") {
      return value[0];
    }

    if (typeof value === "string" && value.trim()) {
      return value;
    }
  }

  if (data.errors) {
    for (const value of Object.values(data.errors)) {
      if (Array.isArray(value) && value.length > 0) {
        return value[0];
      }

      if (typeof value === "string" && value.trim()) {
        return value;
      }
    }
  }

  return null;
}

function getDefaultErrorMessage(status: number): string {
  switch (status) {
    case 400:
      return "Invalid request.";
    case 401:
      return "Authentication required.";
    case 403:
      return "Access restricted.";
    case 404:
      return "Resource not found.";
    case 409:
      return "Conflict detected.";
    case 429:
      return "Too many requests. Please try again later.";
    default:
      return "Something went wrong. Please try again.";
  }
}

export async function parseApiError(response: Response): Promise<ApiClientError> {
  let data: ApiErrorResponse | null = null;

  try {
    data = (await response.json()) as ApiErrorResponse;
  } catch {
    data = null;
  }

  const message = extractErrorMessage(data) || getDefaultErrorMessage(response.status);

  return new ApiClientError(message, response.status, data);
}