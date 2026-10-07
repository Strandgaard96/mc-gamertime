import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { getSeasons, getStats } from "../lib/api";
import { useAuth } from "../lib/AuthContext";

export function useStats(season?: string) {
  const { user } = useAuth();
  return useQuery({
    // Prefix ["stats"] is still what useResults invalidates after a write.
    queryKey: ["stats", season ?? "all"],
    queryFn: () => getStats(season),
    placeholderData: keepPreviousData,
    enabled: !!user,
    refetchInterval: 30_000,
  });
}

export function useSeasons() {
  const { user } = useAuth();
  return useQuery({ queryKey: ["stats", "seasons"], queryFn: getSeasons, enabled: !!user });
}
