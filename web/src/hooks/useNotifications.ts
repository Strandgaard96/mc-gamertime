import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { getNotifications, markNotificationsRead } from "../lib/api";
import { useAuth } from "../lib/AuthContext";
import type { NotificationsResponse } from "../lib/types";

export function useNotifications() {
  const { user } = useAuth();
  return useQuery({
    queryKey: ["notifications"],
    queryFn: getNotifications,
    enabled: !!user,
    refetchInterval: 60_000,
  });
}

export function useMarkNotificationsRead() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: markNotificationsRead,
    onSuccess: () => {
      qc.setQueryData<NotificationsResponse>(["notifications"], (old) =>
        old ? { ...old, unreadCount: 0 } : old,
      );
    },
  });
}
