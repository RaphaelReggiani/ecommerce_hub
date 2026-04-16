import { QueryClient } from "@tanstack/react-query";

import { CACHE_TIMES } from "@/lib/constants/cache";

export function createQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: 1,
        refetchOnWindowFocus: false,
        refetchOnReconnect: true,
        staleTime: CACHE_TIMES.mediumStaleTimeMs,
        gcTime: CACHE_TIMES.gcTimeMs,
      },
      mutations: {
        retry: 0,
      },
    },
  });
}