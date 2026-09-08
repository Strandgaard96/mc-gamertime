import { Bell } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { useMarkNotificationsRead, useNotifications } from "../hooks/useNotifications";
import { formatDate } from "../lib/utils";

export function NotificationBell() {
  const { data } = useNotifications();
  const markRead = useMarkNotificationsRead();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, [open]);

  const notifications = data?.notifications ?? [];
  const unreadCount = data?.unreadCount ?? 0;

  function toggle() {
    setOpen((wasOpen) => {
      if (!wasOpen && unreadCount > 0) markRead.mutate();
      return !wasOpen;
    });
  }

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={toggle}
        className="relative text-muted-foreground hover:text-foreground transition-colors"
        title="Notifications"
        aria-label={
          unreadCount > 0 ? `Notifications, ${unreadCount} unread` : "Notifications, none unread"
        }
        aria-expanded={open}
        aria-haspopup="menu"
      >
        <Bell size={16} />
        {unreadCount > 0 && (
          <span
            aria-hidden="true"
            className="absolute -top-1.5 -right-1.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-primary px-1 text-[10px] font-bold text-primary-foreground"
          >
            {unreadCount}
          </span>
        )}
      </button>
      {open && (
        <div className="absolute right-0 top-full mt-2 w-72 max-h-96 overflow-y-auto bg-card border rounded-lg p-2 z-50 shadow-lg">
          {notifications.length === 0 ? (
            <p className="text-sm text-muted-foreground p-3">No notifications yet</p>
          ) : (
            notifications.map((n) => (
              <div key={n.pk} className="flex items-start gap-2 p-2 rounded-md hover:bg-muted/50">
                <span className="text-xl shrink-0">{n.icon}</span>
                <div className="flex flex-col">
                  <span className="text-sm font-medium">{n.label}</span>
                  <span className="text-xs text-muted-foreground">{n.description}</span>
                  <span className="text-xs text-muted-foreground">
                    {n.gameName} · {formatDate(n.createdAt)}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
