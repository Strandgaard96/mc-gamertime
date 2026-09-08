import { useMemo } from "react";
import { useResults } from "./useResults";

interface GameStats {
  playCounts: Record<string, number>;
  lastPlayedDates: Record<string, string>;
  isLoading: boolean;
}

export function useGameStats(): GameStats {
  const { data: results = [], isLoading } = useResults();

  const playCounts = useMemo(() => {
    return results.reduce(
      (acc, result) => {
        // If we've seen this game before, add 1. If not, start it at 1.
        acc[result.gameId] = (acc[result.gameId] || 0) + 1;
        return acc;
      },
      {} as Record<string, number>,
    );
  }, [results]);

  const lastPlayedDates = useMemo(() => {
    return results.reduce(
      (acc, result) => {
        const current = acc[result.gameId];

        // If we don't have a date for this game yet, OR the current result's
        // date is newer than the saved one, update the dictionary.
        if (!current || result.date > current) {
          acc[result.gameId] = result.date;
        }

        return acc;
      },
      {} as Record<string, string>, // Starts as an empty object
    );
  }, [results]);

  return { playCounts, lastPlayedDates, isLoading };
}
