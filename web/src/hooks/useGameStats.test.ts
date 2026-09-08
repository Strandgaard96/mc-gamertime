import { renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import type { Result } from "../lib/types";
import { useGameStats } from "./useGameStats";
import { useResults } from "./useResults";

vi.mock("./useResults");

function mockResults(results: Partial<Result>[], isLoading = false) {
  vi.mocked(useResults).mockReturnValue({ data: results, isLoading } as any);
}

beforeEach(() => {
  vi.mocked(useResults).mockReset();
});

describe("useGameStats", () => {
  it("returns empty maps while loading with no data", () => {
    vi.mocked(useResults).mockReturnValue({ data: undefined, isLoading: true } as any);

    const { result } = renderHook(() => useGameStats());

    expect(result.current.isLoading).toBe(true);
    expect(result.current.playCounts).toEqual({});
    expect(result.current.lastPlayedDates).toEqual({});
  });

  it("counts plays per game", () => {
    mockResults([
      { gameId: "catan", date: "2026-01-01" },
      { gameId: "catan", date: "2026-01-02" },
      { gameId: "azul", date: "2026-01-03" },
    ]);

    const { result } = renderHook(() => useGameStats());

    expect(result.current.playCounts).toEqual({ catan: 2, azul: 1 });
    expect(result.current.isLoading).toBe(false);
  });

  it("keeps the newest date per game regardless of result order", () => {
    mockResults([
      { gameId: "catan", date: "2026-03-10" },
      { gameId: "catan", date: "2026-01-05" },
      { gameId: "catan", date: "2026-02-20" },
      { gameId: "azul", date: "2025-12-31" },
    ]);

    const { result } = renderHook(() => useGameStats());

    expect(result.current.lastPlayedDates).toEqual({ catan: "2026-03-10", azul: "2025-12-31" });
  });

  it("does not list games that have never been played", () => {
    mockResults([{ gameId: "catan", date: "2026-01-01" }]);

    const { result } = renderHook(() => useGameStats());

    expect(result.current.playCounts).not.toHaveProperty("azul");
    expect(result.current.lastPlayedDates).not.toHaveProperty("azul");
  });

  it("memoizes derived maps while the results reference is unchanged", () => {
    const results = [{ gameId: "catan", date: "2026-01-01" }];
    mockResults(results);

    const { result, rerender } = renderHook(() => useGameStats());
    const first = result.current;
    rerender();

    expect(result.current.playCounts).toBe(first.playCounts);
    expect(result.current.lastPlayedDates).toBe(first.lastPlayedDates);
  });
});
