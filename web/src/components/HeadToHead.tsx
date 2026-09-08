import { motion } from "motion/react";
import type { HeadToHead as H2H } from "../lib/types";

interface Props {
  entries: H2H[];
}

export function HeadToHead({ entries }: Props) {
  if (entries.length === 0)
    return <p className="text-muted-foreground text-sm">No head-to-head data yet.</p>;

  return (
    <div className="space-y-4">
      {entries.map((e, i) => {
        const total = e.p1Wins + e.p2Wins;
        const p1Pct = total === 0 ? 50 : (e.p1Wins / total) * 100;
        const p1Winning = e.p1Wins > e.p2Wins;
        const p2Winning = e.p2Wins > e.p1Wins;
        return (
          <div key={`${e.p1Id}-${e.p2Id}`} className="space-y-1.5">
            <div className="flex items-center justify-between text-sm">
              <span
                className={`font-medium ${p1Winning ? "text-foreground" : "text-muted-foreground"}`}
              >
                {e.p1Name}
              </span>
              <span className="text-xs text-muted-foreground font-mono tabular-nums">
                {e.p1Wins} – {e.p2Wins}
              </span>
              <span
                className={`font-medium text-right ${p2Winning ? "text-foreground" : "text-muted-foreground"}`}
              >
                {e.p2Name}
              </span>
            </div>
            <div className="h-2 rounded-full bg-muted overflow-hidden flex">
              <motion.div
                className="h-full rounded-l-full bg-primary"
                initial={{ width: 0 }}
                animate={{ width: `${p1Pct}%` }}
                transition={{ duration: 0.6, ease: "easeOut", delay: i * 0.08 }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
