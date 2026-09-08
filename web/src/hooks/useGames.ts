import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { deleteGame, getGames, updateGame } from "../lib/api";
import { useAuth } from "../lib/AuthContext";

export function useGames() {
  const { user } = useAuth();
  return useQuery({ queryKey: ["games"], queryFn: getGames, enabled: !!user });
}

export function useDeleteGame() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteGame(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["games"] });
      toast.success("Game removed");
    },
    onError: (err) =>
      toast.error(err instanceof Error && err.message ? err.message : "Failed to remove game"),
  });
}

export function useUpdateGame() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Parameters<typeof updateGame>[1] }) =>
      updateGame(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["games"] });
      toast.success("Game updated");
    },
    onError: (err) =>
      toast.error(err instanceof Error && err.message ? err.message : "Failed to update game"),
  });
}
