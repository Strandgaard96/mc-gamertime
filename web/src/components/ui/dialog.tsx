import { X } from "lucide-react";
import { type ReactNode, useEffect, useId, useRef } from "react";
import { createPortal } from "react-dom";
import { cn } from "../../lib/utils";

interface DialogProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  children: ReactNode;
  className?: string;
}

/**
 * Modal dialog on the native <dialog> element.
 *
 * showModal() is what supplies the modal behaviour a hand-rolled overlay has to
 * reimplement badly: Escape to dismiss, a focus trap, inertness for everything
 * behind it, and placement in the top layer so no z-index can cover it.
 *
 * Two consequences worth knowing. Escape closes the element natively without
 * telling React, so the `cancel`/`close` events are wired back to onClose or the
 * dialog would stay mounted-but-hidden and refuse to reopen. And because the top
 * layer sits above everything, body-level toasts render behind the backdrop
 * while a dialog is open — surface errors inside the dialog, not through toast.
 */
export function Dialog({ open, onClose, title, children, className }: DialogProps) {
  const ref = useRef<HTMLDialogElement>(null);
  const titleId = useId();

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (open && !el.open) {
      // Capture the opener before showModal() moves focus into the dialog.
      const opener = document.activeElement as HTMLElement | null;
      el.showModal();
      return () => opener?.focus?.();
    }
    if (!open && el.open) el.close();
  }, [open]);

  if (!open) return null;

  return createPortal(
    <dialog
      ref={ref}
      aria-labelledby={title ? titleId : undefined}
      onCancel={(e) => {
        // Escape: let onClose drive the unmount so React state stays in step.
        e.preventDefault();
        onClose();
      }}
      onClose={onClose}
      onPointerDown={(e) => {
        // The backdrop is the only part of the element the pointer can reach —
        // padding and scrolling live on the inner wrapper — so a hit on the
        // dialog itself means the user clicked outside the content.
        if (e.target === ref.current) onClose();
      }}
      className={cn(
        "m-auto w-[calc(100%-2rem)] max-w-md bg-transparent p-0 text-card-foreground",
        "backdrop:bg-black/60 backdrop:backdrop-blur-xs",
        "animate-in fade-in zoom-in-95 slide-in-from-bottom-2 duration-200",
        className,
      )}
    >
      <div className="max-h-[85vh] overflow-y-auto rounded-xl border bg-card p-6 shadow-2xl">
        <div className={cn("flex items-center mb-5", title ? "justify-between" : "justify-end")}>
          {title && (
            <h2 id={titleId} className="text-xl font-semibold tracking-tight">
              {title}
            </h2>
          )}
          <button
            type="button"
            onClick={onClose}
            className="rounded-full p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors focus:outline-hidden focus:ring-2 focus:ring-ring"
          >
            <X size={18} />
            <span className="sr-only">Close</span>
          </button>
        </div>
        {children}
      </div>
    </dialog>,
    document.body,
  );
}
