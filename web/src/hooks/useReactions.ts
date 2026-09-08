import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { addComment, deleteComment, getReactions, toggleReaction } from "../lib/api";

export function useReactions() {
  return useQuery({ queryKey: ["reactions"], queryFn: getReactions });
}

export function useToggleReaction() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ sessionPk, emoji }: { sessionPk: string; emoji: string }) =>
      toggleReaction(sessionPk, emoji),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["reactions"] }),
    onError: () => toast.error("Failed to update reaction"),
  });
}

export function useAddComment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ sessionPk, text }: { sessionPk: string; text: string }) =>
      addComment(sessionPk, text),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["reactions"] });
      toast.success("Comment added");
    },
    onError: () => toast.error("Failed to add comment"),
  });
}

export function useDeleteComment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteComment(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["reactions"] });
      toast.success("Comment deleted");
    },
    onError: () => toast.error("Failed to delete comment"),
  });
}
