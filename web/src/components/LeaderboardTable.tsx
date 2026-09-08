import { Flame } from "lucide-react";
import { motion } from "motion/react";
import { Link } from "react-router-dom";
import type { LeaderboardEntry, StreakEntry } from "../lib/types";
import { Avatar } from "./Avatar";

interface Props {
  entries: LeaderboardEntry[];
  streaks?: StreakEntry[];
  avatarMap?: Record<string, string | undefined>;
}

const containerVariants = {
  animate: { transition: { staggerChildren: 0.04 } },
};

const rowVariants = {
  initial: { opacity: 0, y: 8 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.2 } },
};

export function LeaderboardTable({ entries, streaks = [], avatarMap = {} }: Props) {
  const streakMap = Object.fromEntries(streaks.map((s) => [s.playerId, s.current]));

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b text-muted-foreground">
            <th className="pb-2 text-left w-8">#</th>
            <th className="pb-2 text-left">Player</th>
            <th className="pb-2 text-right">Rating</th>
            <th className="pb-2 text-right">Wins</th>
            <th className="pb-2 text-right">Played</th>
            <th className="pb-2 text-right">Win %</th>
          </tr>
        </thead>
        <motion.tbody variants={containerVariants} initial="initial" animate="animate">
          {entries.map((e, i) => {
            const streak = streakMap[e.playerId] ?? 0;
            return (
              <motion.tr
                key={e.playerId}
                variants={rowVariants}
                className={`border-b last:border-0 hover:bg-muted/30 transition-colors ${i === 0 ? "animate-pulse-gold" : ""}`}
              >
                <td className="py-3 pr-3">
                  <span
                    className={`inline-flex items-center justify-center w-6 h-6 rounded-full text-[11px] font-bold ${
                      i === 0
                        ? "bg-yellow-400/20 text-yellow-400 ring-1 ring-yellow-400/40"
                        : i === 1
                          ? "bg-slate-400/20 text-slate-400 ring-1 ring-slate-400/40"
                          : i === 2
                            ? "bg-amber-700/20 text-amber-600 ring-1 ring-amber-700/30"
                            : "bg-muted/60 text-muted-foreground"
                    }`}
                  >
                    {i + 1}
                  </span>
                </td>
                <td className="py-3">
                  <div className="flex items-center gap-2">
                    <Avatar name={e.name} size="sm" imageUrl={avatarMap[e.playerId]} />
                    <div>
                      <Link
                        to={`/players/${e.playerId}`}
                        className="font-medium hover:text-primary transition-colors"
                      >
                        {e.name}
                      </Link>
                      {streak > 0 && (
                        <div className="flex items-center gap-0.5 text-xs text-orange-400 mt-0.5">
                          <Flame size={10} />
                          <span>{streak}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </td>
                <td className="py-3 text-right font-semibold tabular-nums">{e.rating}</td>
                <td className="py-3 text-right font-medium">{e.wins}</td>
                <td className="py-3 text-right text-muted-foreground">{e.played}</td>
                <td className="py-3 text-right">
                  <div className="flex flex-col items-end gap-1">
                    <span>{(e.winRate * 100).toFixed(0)}%</span>
                    <div className="w-14 h-1 rounded-full bg-muted overflow-hidden">
                      <motion.div
                        className="h-full rounded-full bg-primary"
                        initial={{ width: 0 }}
                        animate={{ width: `${Math.round(e.winRate * 100)}%` }}
                        transition={{ duration: 0.6, ease: "easeOut", delay: i * 0.04 }}
                      />
                    </div>
                  </div>
                </td>
              </motion.tr>
            );
          })}
        </motion.tbody>
      </table>
    </div>
  );
}
