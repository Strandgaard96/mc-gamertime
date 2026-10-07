import { createPhoto, requestPhotoUpload } from "./api";
import type { PhotoItem } from "./types";

export const MAX_PHOTOS = 6;
const MAX_EDGE = 2048;
const QUALITY = 0.85;

function toBlob(canvas: HTMLCanvasElement, type: string): Promise<Blob> {
  return new Promise((resolve, reject) =>
    canvas.toBlob(
      (b) => (b ? resolve(b) : reject(new Error("Could not encode image"))),
      type,
      QUALITY,
    ),
  );
}

/**
 * Downscale to MAX_EDGE on the long side and re-encode. Re-encoding through a
 * canvas drops all EXIF (including GPS); decoding with imageOrientation
 * "from-image" bakes the camera rotation in first so the photo stays upright.
 * Older Safari ignores "image/webp" and returns PNG — far larger — so fall
 * back to JPEG. The upload uses the blob's real type.
 */
export async function preparePhoto(file: File): Promise<Blob> {
  const bitmap = await createImageBitmap(file, { imageOrientation: "from-image" });
  const scale = Math.min(1, MAX_EDGE / Math.max(bitmap.width, bitmap.height));
  const canvas = document.createElement("canvas");
  canvas.width = Math.round(bitmap.width * scale);
  canvas.height = Math.round(bitmap.height * scale);
  canvas.getContext("2d")?.drawImage(bitmap, 0, 0, canvas.width, canvas.height);
  bitmap.close?.();
  const webp = await toBlob(canvas, "image/webp");
  return webp.type === "image/webp" ? webp : toBlob(canvas, "image/jpeg");
}

export async function uploadSessionPhoto(sessionPk: string, blob: Blob): Promise<PhotoItem> {
  const { uploadUrl, key } = await requestPhotoUpload(sessionPk, blob.type);
  const res = await fetch(uploadUrl, {
    method: "PUT",
    body: blob,
    headers: { "Content-Type": blob.type },
  });
  if (!res.ok) throw new Error(`Photo upload failed (${res.status})`);
  return createPhoto(sessionPk, key);
}
