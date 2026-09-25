import { useQuery } from "@tanstack/react-query";
import { getPublicSettings } from "../lib/api";

// Same default the API returns when no display name is set; also covers the
// moment before settings load.
const DEFAULT_DISPLAY_NAME = "MC GamerTime";

export function useDisplayName(): string {
  const { data } = usePublicSettings();
  return data?.displayName ?? DEFAULT_DISPLAY_NAME;
}

export function usePublicSettings() {
  return useQuery({
    queryKey: ["settings", "public"],
    queryFn: getPublicSettings,
  });
}
