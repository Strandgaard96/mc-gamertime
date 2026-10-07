import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { deletePhoto } from "../lib/api";
import { preparePhoto, uploadSessionPhoto } from "../lib/photos";

export function useAddPhoto() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ sessionPk, file }: { sessionPk: string; file: File }) =>
      uploadSessionPhoto(sessionPk, await preparePhoto(file)),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["reactions"] }),
    onError: () => toast.error("Photo upload failed"),
  });
}

export function useDeletePhoto() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deletePhoto(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["reactions"] });
      toast.success("Photo deleted");
    },
    onError: () => toast.error("Failed to delete photo"),
  });
}
