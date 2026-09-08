import { useRegisterSW } from "virtual:pwa-register/react";
import { useEffect } from "react";
import { toast } from "sonner";

export function ReloadPrompt() {
  const {
    needRefresh: [needRefresh],
    updateServiceWorker,
  } = useRegisterSW({
    onRegisterError(error) {
      console.warn("Service worker registration failed", error);
    },
  });

  useEffect(() => {
    if (!needRefresh) return;
    toast("New version available", {
      id: "sw-update",
      duration: Infinity,
      action: {
        label: "Update",
        onClick: () => {
          void updateServiceWorker(true);
        },
      },
    });
  }, [needRefresh, updateServiceWorker]);

  return null;
}
