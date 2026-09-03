import { useQuery } from "@tanstack/react-query";
import { getStats } from "../lib/api";
import { useAuth } from "../lib/AuthContext";

export function useStats() {
  const { user } = useAuth();
  return useQuery({
    queryKey: ["stats"],
    queryFn: getStats,
    enabled: !!user,
    refetchInterval: 30_000,
  });
}
