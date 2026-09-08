import { useQuery } from "@tanstack/react-query";
import { getPlayers } from "../lib/api";
import { useAuth } from "../lib/AuthContext";

export function usePlayers() {
  const { user } = useAuth();
  return useQuery({
    queryKey: ["players"],
    queryFn: getPlayers,
    enabled: !!user,
  });
}
