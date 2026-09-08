import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { createPost, deletePost, getPosts, updatePost } from "../lib/api";
import { useAuth } from "../lib/AuthContext";
import type { Post } from "../lib/types";

export function usePosts() {
  const { user } = useAuth();
  return useQuery({ queryKey: ["posts"], queryFn: getPosts, enabled: !!user });
}

export function useCreatePost() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createPost,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["posts"] });
      toast.success("Post published");
    },
    onError: () => toast.error("Failed to publish post"),
  });
}

export function useUpdatePost() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Post> }) => updatePost(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["posts"] });
      toast.success("Post saved");
    },
    onError: () => toast.error("Failed to save post"),
  });
}

export function useDeletePost() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deletePost(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["posts"] });
      toast.success("Post deleted");
    },
    onError: () => toast.error("Failed to delete post"),
  });
}
