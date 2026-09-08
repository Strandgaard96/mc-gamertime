import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import {
  createRecommended,
  deleteRecommended,
  getRecommended,
  getRecommendedDetail,
  updateRecommended,
} from "../lib/api";

export function useRecommended() {
  return useQuery({ queryKey: ["recommended"], queryFn: getRecommended });
}

export function useRecommendedDetail(id: string | undefined) {
  return useQuery({
    queryKey: ["recommended", id],
    queryFn: () => getRecommendedDetail(id!),
    enabled: !!id,
  });
}

export function useCreateRecommended() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createRecommended,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["recommended"] });
      toast.success("Recommendation added");
    },
    onError: () => toast.error("Failed to add recommendation"),
  });
}

export function useUpdateRecommended() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string;
      data: { blurb?: string; tags?: string[]; bestFor?: string; order?: number; content?: string };
    }) => updateRecommended(id, data),
    onSuccess: (_data, { id }) => {
      qc.invalidateQueries({ queryKey: ["recommended"] });
      qc.invalidateQueries({ queryKey: ["recommended", id] });
      toast.success("Recommendation updated");
    },
    onError: () => toast.error("Failed to update recommendation"),
  });
}

export function useDeleteRecommended() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteRecommended(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["recommended"] });
      toast.success("Recommendation removed");
    },
    onError: () => toast.error("Failed to remove recommendation"),
  });
}
