import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import confetti from "canvas-confetti";
import { toast } from "sonner";
import { addResult, deleteResult, getResults, updateResult } from "../lib/api";
import { useAuth } from "../lib/AuthContext";
import type { Result } from "../lib/types";

export function useResults() {
  const { user } = useAuth();
  return useQuery({
    queryKey: ["results"],
    queryFn: getResults,
    enabled: !!user,
    refetchInterval: 30_000,
  });
}

export function useAddResult() {
  const qc = useQueryClient();

  return useMutation({
    mutationFn: (result: Omit<Result, "pk" | "createdAt" | "milestone" | "newAchievements">) =>
      addResult(result),

    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ["results"] });
      qc.invalidateQueries({ queryKey: ["stats"] });
      qc.invalidateQueries({ queryKey: ["notifications"] });
      confetti({
        particleCount: 140,
        spread: 90,
        origin: { y: 0.3 },
        colors: ["#f5a623", "#ffffff", "#fde68a"],
      });
      toast.success("Game logged!");
      if (data?.milestone) {
        setTimeout(() => toast(data.milestone!, { duration: 6000 }), 800);
      }
      (data?.newAchievements ?? []).forEach((a, i) => {
        setTimeout(
          () =>
            toast.success(`${a.icon} ${a.playerName} earned ${a.label} — ${a.description}`, {
              duration: 6000,
            }),
          1200 + i * 600,
        );
      });
    },

    onError: (err) => toast.error(err instanceof Error ? err.message : "Failed to log game"),
  });
}

export function useDeleteResult() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteResult(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["results"] });
      qc.invalidateQueries({ queryKey: ["stats"] });
      qc.invalidateQueries({ queryKey: ["playerStats"] });
      toast.success("Result deleted");
    },
    onError: () => toast.error("Failed to delete result"),
  });
}

export function useUpdateResult() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string;
      data: Partial<Omit<Result, "pk" | "createdAt" | "milestone">>;
    }) => updateResult(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["results"] });
      qc.invalidateQueries({ queryKey: ["stats"] });
      qc.invalidateQueries({ queryKey: ["playerStats"] });
      toast.success("Result updated");
    },
    onError: (err) => toast.error(err instanceof Error ? err.message : "Failed to update result"),
  });
}
