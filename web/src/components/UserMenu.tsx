import { LogOut } from "lucide-react";
import type { ReactNode } from "react";
import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { cn } from "../lib/utils";
import { Avatar } from "./Avatar";

export interface UserMenuItem {
  to: string;
  label: string;
  icon: ReactNode;
}

interface UserMenuProps {
  displayName: string;
  profileTo: string;
  avatarUrl?: string;
  items: UserMenuItem[];
  onLogout: () => void;
  /** Show the display name next to the avatar (desktop has room, mobile doesn't). */
  showName?: boolean;
}

/**
 * Account menu behind the avatar. Holds everything that doesn't earn a slot in
 * the five-item bottom nav — the profile link, secondary destinations, the
 * admin-only pages and Sign out.
 */
export function UserMenu({
  displayName,
  profileTo,
  avatarUrl,
  items,
  onLogout,
  showName = false,
}: UserMenuProps) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!open) return;
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    function handleKey(e: KeyboardEvent) {
      if (e.key === "Escape") {
        setOpen(false);
        buttonRef.current?.focus();
      }
    }
    document.addEventListener("mousedown", handleClick);
    document.addEventListener("keydown", handleKey);
    return () => {
      document.removeEventListener("mousedown", handleClick);
      document.removeEventListener("keydown", handleKey);
    };
  }, [open]);

  const itemClass =
    "flex items-center gap-2 w-full rounded-md px-2 py-2 text-sm text-left text-muted-foreground hover:bg-muted/50 hover:text-foreground transition-colors";

  return (
    <div className="relative" ref={ref}>
      <button
        ref={buttonRef}
        type="button"
        onClick={() => setOpen((wasOpen) => !wasOpen)}
        aria-label={`Account menu for ${displayName}`}
        aria-haspopup="menu"
        aria-expanded={open}
        className={cn(
          "flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors",
        )}
      >
        <Avatar name={displayName} imageUrl={avatarUrl} size="sm" />
        {showName && displayName}
      </button>
      {open && (
        <div
          role="menu"
          aria-label="Account"
          className="absolute right-0 top-full mt-2 w-52 bg-card border rounded-lg p-1.5 z-50 shadow-lg"
        >
          <Link
            role="menuitem"
            to={profileTo}
            onClick={() => setOpen(false)}
            className={cn(itemClass, "font-medium text-foreground")}
          >
            {displayName}
          </Link>
          <div className="my-1 border-t" />
          {items.map(({ to, label, icon }) => (
            <Link
              key={to}
              role="menuitem"
              to={to}
              onClick={() => setOpen(false)}
              className={itemClass}
            >
              {icon}
              {label}
            </Link>
          ))}
          <div className="my-1 border-t" />
          <button role="menuitem" type="button" onClick={onLogout} className={itemClass}>
            <LogOut size={16} />
            Sign out
          </button>
        </div>
      )}
    </div>
  );
}
