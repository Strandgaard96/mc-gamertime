import { useQuery } from "@tanstack/react-query";
import { getPublicSettings } from "../lib/api";

export function usePublicSettings() {
  return useQuery({
    queryKey: ["settings", "public"],
    queryFn: getPublicSettings,
  });
}
