import { useQuery } from "@tanstack/react-query";
import { getPlayerStats } from "../lib/api";

export function usePlayerStats(playerId: string | undefined) {
  return useQuery({
    queryKey: ["playerStats", playerId],
    queryFn: () => getPlayerStats(playerId!),
    enabled: !!playerId,
    staleTime: 60_000,
  });
}
