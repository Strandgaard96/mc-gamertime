import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";
import type { StatsResponse } from "../lib/types";
import { useStats } from "./useStats";

vi.mock("../lib/AuthContext", () => ({ useAuth: () => ({ user: { sub: "u" } }) }));

const getStats = vi.fn();
vi.mock("../lib/api", () => ({ getStats: (s?: string) => getStats(s), getSeasons: vi.fn() }));

describe("useStats", () => {
  it("keeps previous data (not isLoading) while a new season loads", async () => {
    const all = { leaderboard: [] } as unknown as StatsResponse;
    getStats.mockResolvedValueOnce(all);
    const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    const wrapper = ({ children }: { children: ReactNode }) => (
      <QueryClientProvider client={qc}>{children}</QueryClientProvider>
    );
    const { result, rerender } = renderHook(({ s }) => useStats(s), {
      wrapper,
      initialProps: { s: undefined as string | undefined },
    });
    await waitFor(() => expect(result.current.data).toBe(all));

    getStats.mockReturnValueOnce(new Promise(() => {}));
    rerender({ s: "2026-Q3" });

    expect(result.current.isLoading).toBe(false);
    expect(result.current.data).toBe(all);
  });
});
