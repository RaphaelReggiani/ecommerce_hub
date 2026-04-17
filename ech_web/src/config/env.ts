type AppEnv = "development" | "test" | "production";

function getRequiredEnv(name: string, fallback?: string): string {
  const value = process.env[name] ?? fallback;

  if (!value) {
    throw new Error(`Missing required environment variable: ${name}`);
  }

  return value;
}

function getAppEnv(): AppEnv {
  const value =
    process.env.NEXT_PUBLIC_APP_ENV ??
    process.env.NODE_ENV ??
    "development";

  if (value === "development" || value === "test" || value === "production") {
    return value;
  }

  return "development";
}

export const env = {
  APP_NAME: getRequiredEnv("NEXT_PUBLIC_APP_NAME", "E-commerce Hub"),
  APP_ENV: getAppEnv(),
  API_BASE_URL: getRequiredEnv(
    "NEXT_PUBLIC_API_BASE_URL",
    "http://127.0.0.1:8000/api/v1",
  ),
} as const;