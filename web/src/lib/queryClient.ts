import { QueryClient } from "@tanstack/react-query";

// A 4xx is an answer, not a blip. Retrying one just multiplies the
// console noise — six failed /recommended calls on the logged-out
// landing page when PUBLIC_RECOMMENDED_ENABLED is unset, for instance.
export function shouldRetryQuery(failureCount: number, error: unknown): boolean {
  const status = (error as { status?: number }).status;
  if (status !== undefined && status >= 400 && status < 500) return false;
  return failureCount < 3;
}

export function createQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 1000 * 60 * 2,
        retry: shouldRetryQuery,
      },
    },
  });
}
