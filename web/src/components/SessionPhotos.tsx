import { ChevronLeft, ChevronRight, ImagePlus, Trash2 } from "lucide-react";
import { type ChangeEvent, useEffect, useId, useMemo, useState } from "react";
import { useAddPhoto, useDeletePhoto } from "../hooks/usePhotos";
import { useReactions } from "../hooks/useReactions";
import { useAuth } from "../lib/AuthContext";
import { MAX_PHOTOS } from "../lib/photos";
import type { PhotoItem } from "../lib/types";
import { Dialog } from "./ui/dialog";

export function SessionPhotos({ sessionPk }: { sessionPk: string }) {
  const { user } = useAuth();
  const { data: items = [] } = useReactions();
  const addPhoto = useAddPhoto();
  const deletePhoto = useDeletePhoto();
  const inputId = useId();
  const [open, setOpen] = useState<number | null>(null);

  const photos = useMemo(
    () =>
      items
        .filter((i): i is PhotoItem => i.type === "photo" && i.sessionPk === sessionPk)
        .sort((a, b) => a.createdAt.localeCompare(b.createdAt)),
    [items, sessionPk],
  );
  const canDelete = (p: PhotoItem) => p.uploaderId === user?.sub || user?.role === "admin";
  const current = open != null ? photos[open] : undefined;

  function handleFile(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (file) addPhoto.mutate({ sessionPk, file });
  }

  function step(delta: number) {
    setOpen((o) =>
      o == null || photos.length === 0 ? o : (o + delta + photos.length) % photos.length,
    );
  }

  // showModal() focuses the dialog's close button, outside the image wrapper, so
  // arrow keys are listened for on the document while the lightbox is open.
  const lightboxOpen = current != null;
  useEffect(() => {
    if (!lightboxOpen) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "ArrowLeft") step(-1);
      if (e.key === "ArrowRight") step(1);
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  });

  if (photos.length === 0 && !user) return null;

  return (
    <div className="mt-2 flex flex-wrap items-center gap-1.5">
      {photos.map((p, i) => (
        <div key={p.pk} className="relative">
          <button
            type="button"
            onClick={() => setOpen(i)}
            className="block size-14 overflow-hidden rounded-md border bg-muted"
          >
            <img
              src={p.imageUrl}
              alt={`Photo by ${p.uploaderName}`}
              loading="lazy"
              className="size-full object-cover"
            />
          </button>
          {canDelete(p) && (
            <button
              type="button"
              aria-label="Delete photo"
              onClick={() => deletePhoto.mutate(p.pk)}
              disabled={deletePhoto.isPending}
              className="absolute -right-1.5 -top-1.5 grid size-6 place-items-center rounded-full border bg-card text-muted-foreground hover:text-destructive"
            >
              <Trash2 size={12} aria-hidden="true" />
            </button>
          )}
        </div>
      ))}
      {user && photos.length < MAX_PHOTOS && (
        <label
          htmlFor={inputId}
          role="button"
          aria-label="Add photo"
          aria-busy={addPhoto.isPending}
          className="grid size-14 cursor-pointer place-items-center rounded-md border border-dashed text-muted-foreground hover:border-primary/40 hover:text-foreground"
        >
          <ImagePlus
            size={18}
            aria-hidden="true"
            className={addPhoto.isPending ? "animate-pulse" : ""}
          />
          <input
            id={inputId}
            type="file"
            accept="image/*"
            className="sr-only"
            onChange={handleFile}
            disabled={addPhoto.isPending}
          />
        </label>
      )}
      <Dialog
        open={current != null}
        onClose={() => setOpen(null)}
        title={current ? `Photo by ${current.uploaderName}` : undefined}
        className="max-w-3xl"
      >
        {current && (
          <div className="flex items-center gap-2">
            {photos.length > 1 && (
              <button
                type="button"
                aria-label="Previous photo"
                onClick={() => step(-1)}
                className="p-2"
              >
                <ChevronLeft aria-hidden="true" />
              </button>
            )}
            <img
              src={current.imageUrl}
              alt={`Photo by ${current.uploaderName}`}
              className="max-h-[70vh] w-full rounded-md object-contain"
            />
            {photos.length > 1 && (
              <button type="button" aria-label="Next photo" onClick={() => step(1)} className="p-2">
                <ChevronRight aria-hidden="true" />
              </button>
            )}
          </div>
        )}
      </Dialog>
    </div>
  );
}
