import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import type { SeasonSummary } from "../lib/types";
import { SeasonScope } from "./SeasonScope";

const SEASONS: SeasonSummary[] = [
  { id: "2026-Q4", label: "Q4 2026", finished: false, champion: null },
  { id: "2026-Q3", label: "Q3 2026", finished: true, champion: { playerId: "a", name: "Alice" } },
  { id: "2026-Q2", label: "Q2 2026", finished: true, champion: null },
];

describe("SeasonScope", () => {
  it("switching to Season selects the newest (current) season", () => {
    const onChange = vi.fn();
    render(<SeasonScope seasons={SEASONS} value={undefined} onChange={onChange} />);
    fireEvent.click(screen.getByRole("button", { name: "Season" }));
    expect(onChange).toHaveBeenCalledWith("2026-Q4");
  });

  it("shows pending champion copy for the current season", () => {
    render(<SeasonScope seasons={SEASONS} value="2026-Q4" onChange={() => {}} />);
    expect(screen.getByText(/Champion decided at end of quarter/)).toBeInTheDocument();
  });

  it("shows the champion of a finished season", () => {
    render(<SeasonScope seasons={SEASONS} value="2026-Q3" onChange={() => {}} />);
    expect(screen.getByText(/Alice/)).toBeInTheDocument();
  });

  it("shows no-qualifier copy for a finished season without champion", () => {
    render(<SeasonScope seasons={SEASONS} value="2026-Q2" onChange={() => {}} />);
    expect(screen.getByText(/No qualifying champion/)).toBeInTheDocument();
  });

  it("All-time clears the season", () => {
    const onChange = vi.fn();
    render(<SeasonScope seasons={SEASONS} value="2026-Q3" onChange={onChange} />);
    fireEvent.click(screen.getByRole("button", { name: "All-time" }));
    expect(onChange).toHaveBeenCalledWith(undefined);
  });
});
