import { Trophy } from "lucide-react";
import { useId } from "react";
import type { SeasonSummary } from "../lib/types";
import { cn } from "../lib/utils";

interface Props {
  seasons: SeasonSummary[];
  /** Selected season id, or undefined for all-time. */
  value: string | undefined;
  onChange: (season: string | undefined) => void;
}

export function SeasonScope({ seasons, value, onChange }: Props) {
  const selectId = useId();
  const selected = seasons.find((s) => s.id === value);
  const tab = (active: boolean) =>
    cn(
      "px-3 py-1.5 text-sm rounded-md transition-colors min-h-9",
      active ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:text-foreground",
    );

  return (
    <div className="flex flex-wrap items-center gap-3">
      <div
        className="inline-flex rounded-lg border p-0.5"
        role="group"
        aria-label="Leaderboard scope"
      >
        <button
          type="button"
          aria-pressed={value === undefined}
          className={tab(value === undefined)}
          onClick={() => onChange(undefined)}
        >
          All-time
        </button>
        <button
          type="button"
          aria-pressed={value !== undefined}
          className={tab(value !== undefined)}
          onClick={() => value === undefined && seasons[0] && onChange(seasons[0].id)}
        >
          Season
        </button>
      </div>
      {value !== undefined && (
        <>
          <label htmlFor={selectId} className="sr-only">
            Season
          </label>
          <select
            id={selectId}
            className="rounded-md border border-input bg-background px-3 py-1.5 text-sm"
            value={value}
            onChange={(e) => onChange(e.target.value)}
          >
            {seasons.map((s) => (
              <option key={s.id} value={s.id}>
                {s.label}
              </option>
            ))}
          </select>
          <p className="text-sm text-muted-foreground flex items-center gap-1.5">
            <Trophy size={14} aria-hidden="true" className="text-yellow-400" />
            {!selected || !selected.finished
              ? "Champion decided at end of quarter — min 5 games to qualify"
              : selected.champion
                ? `Champion: ${selected.champion.name}`
                : "No qualifying champion (min 5 games)"}
          </p>
        </>
      )}
    </div>
  );
}
