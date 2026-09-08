import { useState } from "react";
import { toast } from "sonner";
import { getGameUploadUrl } from "../lib/api";

export function useGameImageUpload(initialImageUrl?: string) {
  const [imageUrl, setImageUrl] = useState<string | undefined>(initialImageUrl);
  const [uploading, setUploading] = useState(false);

  async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      const { uploadUrl, imageUrl: newImageUrl } = await getGameUploadUrl(file.name, file.type);
      await fetch(uploadUrl, { method: "PUT", body: file, headers: { "Content-Type": file.type } });
      setImageUrl(newImageUrl);
    } catch (e) {
      console.error("Image upload failed", e);
      toast.error("Image upload failed");
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  }

  return { imageUrl, uploading, handleFileChange, setImageUrl };
}
