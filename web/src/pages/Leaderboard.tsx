import { ChevronDown, ChevronUp, Dices, Flame, Trophy } from "lucide-react";
import { AnimatePresence, motion } from "motion/react";
import { useState } from "react";
import { Link } from "react-router-dom";
import { Avatar } from "../components/Avatar";
import { HeadToHead } from "../components/HeadToHead";
import { LeaderboardTable } from "../components/LeaderboardTable";
import { MonthlyChart } from "../components/MonthlyChart";
import { PageTransition } from "../components/PageTransition";
import { Skeleton } from "../components/ui/skeleton";
import { WinRaceChart } from "../components/WinRaceChart";
import { usePlayers } from "../hooks/usePlayers";
import { useResults } from "../hooks/useResults";
import { useStats } from "../hooks/useStats";
import type { GameStat, LeaderboardEntry } from "../lib/types";
import { pluralize } from "../lib/utils";

const PODIUM = {
  1: {
    border: "border-yellow-400/40",
    bg: "bg-yellow-400/10",
    text: "text-yellow-400",
    platform: "bg-yellow-400/20 h-16",
  },
  2: {
    border: "border-slate-400/40",
    bg: "bg-slate-400/10",
    text: "text-slate-400",
    platform: "bg-slate-400/20 h-10",
  },
  3: {
    border: "border-amber-600/40",
    bg: "bg-amber-600/10",
    text: "text-amber-600",
    platform: "bg-amber-600/20 h-6",
  },
} as const;

const PODIUM_DELAY: Record<1 | 2 | 3, number> = { 1: 0, 2: 0.1, 3: 0.2 };

function PodiumSlot({
  entry,
  rank,
  featured = false,
  avatarMap = {},
}: {
  entry: LeaderboardEntry;
  rank: 1 | 2 | 3;
  featured?: boolean;
  avatarMap?: Record<string, string | undefined>;
}) {
  const c = PODIUM[rank];
  return (
    <motion.div
      className="flex flex-col items-center flex-1 max-w-[130px]"
      initial={{ opacity: 0, y: 40 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: "easeOut", delay: PODIUM_DELAY[rank] }}
    >
      <div className={`w-full rounded-xl border ${c.border} ${c.bg} p-3 text-center mb-0`}>
        <Avatar
          name={entry.name}
          imageUrl={avatarMap[entry.playerId]}
          size={featured ? "lg" : "md"}
          className="mx-auto mb-2"
        />
        <Trophy size={13} className={`mx-auto mb-1 ${c.text}`} />
        <Link
          to={`/players/${entry.playerId}`}
          className={`font-medium text-xs hover:text-primary transition-colors block truncate ${c.text}`}
        >
          {entry.name}
        </Link>
        <div className={`text-xl font-display font-bold ${c.text}`}>{entry.wins}W</div>
        <div className="text-xs text-muted-foreground">{(entry.winRate * 100).toFixed(0)}% WR</div>
      </div>
      <div className={`w-3/4 ${c.platform} rounded-t-md flex items-center justify-center`}>
        <span className={`text-xs font-bold ${c.text}`}>#{rank}</span>
      </div>
    </motion.div>
  );
}

function GameStatCard({ gs }: { gs: GameStat }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="border rounded-lg overflow-hidden">
      <button
        className="w-full flex items-center justify-between p-3 bg-card hover:bg-muted/30 transition-colors text-left"
        onClick={() => setOpen((o) => !o)}
      >
        <div>
          <span className="font-medium">{gs.gameName}</span>
          <span className="text-muted-foreground text-sm ml-2">
            {pluralize(gs.totalPlays, "play")}
          </span>
        </div>
        <div className="flex items-center gap-3 text-sm">
          <span className="text-muted-foreground">
            Top: <span className="text-foreground font-medium">{gs.dominantPlayer.name}</span>
            <span className="text-muted-foreground ml-1">
              ({Math.round(gs.dominantPlayer.winRate * 100)}% WR)
            </span>
          </span>
          {open ? (
            <ChevronUp size={14} className="text-muted-foreground" />
          ) : (
            <ChevronDown size={14} className="text-muted-foreground" />
          )}
        </div>
      </button>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            key="content"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2, ease: "easeInOut" }}
            className="overflow-hidden border-t"
          >
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-muted-foreground bg-muted/20">
                  <th className="py-2 px-3 text-left">Player</th>
                  <th className="py-2 px-3 text-right">Played</th>
                  <th className="py-2 px-3 text-right">Wins</th>
                  <th className="py-2 px-3 text-right">Win %</th>
                </tr>
              </thead>
              <tbody>
                {gs.playerBreakdown.map((p) => (
                  <tr
                    key={p.playerId}
                    className="border-b last:border-0 hover:bg-muted/20 transition-colors"
                  >
                    <td className="py-2 px-3 font-medium">{p.name}</td>
                    <td className="py-2 px-3 text-right text-muted-foreground">{p.played}</td>
                    <td className="py-2 px-3 text-right">{p.wins}</td>
                    <td className="py-2 px-3 text-right">
                      <span className={p.winRate >= 0.5 ? "text-primary" : "text-muted-foreground"}>
                        {Math.round(p.winRate * 100)}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {Object.entries(gs.variableStats).map(([varId, v]) => (
              <table key={varId} className="w-full text-sm">
                <thead>
                  <tr className="border-b text-muted-foreground bg-muted/20">
                    <th className="py-2 px-3 text-left">{v.label}</th>
                    <th className="py-2 px-3 text-right">Picked</th>
                    <th className="py-2 px-3 text-right">Pick %</th>
                    <th className="py-2 px-3 text-right">Win %</th>
                    <th className="py-2 px-3 text-right">Avg score</th>
                  </tr>
                </thead>
                <tbody>
                  {v.breakdown.map((b) => (
                    <tr
                      key={b.value}
                      className="border-b last:border-0 hover:bg-muted/20 transition-colors"
                    >
                      <td className="py-2 px-3 font-medium">{b.value}</td>
                      <td className="py-2 px-3 text-right text-muted-foreground">{b.picks}</td>
                      <td className="py-2 px-3 text-right">{Math.round(b.pickRate * 100)}%</td>
                      <td className="py-2 px-3 text-right">
                        <span
                          className={b.winRate >= 0.5 ? "text-primary" : "text-muted-foreground"}
                        >
                          {Math.round(b.winRate * 100)}%
                        </span>
                      </td>
                      <td className="py-2 px-3 text-right text-muted-foreground">
                        {b.avgScore != null ? b.avgScore.toFixed(1) : "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ))}

            {gs.seatStats.length > 0 && (
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-muted-foreground bg-muted/20">
                    <th className="py-2 px-3 text-left">Seat</th>
                    <th className="py-2 px-3 text-right">Plays</th>
                    <th className="py-2 px-3 text-right">Wins</th>
                    <th className="py-2 px-3 text-right">Win %</th>
                  </tr>
                </thead>
                <tbody>
                  {gs.seatStats.map((s) => (
                    <tr
                      key={s.seat}
                      className="border-b last:border-0 hover:bg-muted/20 transition-colors"
                    >
                      <td className="py-2 px-3 font-medium">
                        {s.seat === 1 ? "1st" : `Seat ${s.seat}`}
                      </td>
                      <td className="py-2 px-3 text-right text-muted-foreground">{s.plays}</td>
                      <td className="py-2 px-3 text-right">{s.wins}</td>
                      <td className="py-2 px-3 text-right">
                        <span
                          className={s.winRate >= 0.5 ? "text-primary" : "text-muted-foreground"}
                        >
                          {Math.round(s.winRate * 100)}%
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default function Leaderboard() {
  const { data: stats, isLoading } = useStats();
  const { data: results = [] } = useResults();
  const { data: players = [] } = usePlayers();
  const avatarMap = Object.fromEntries(players.map((p) => [p.pk, p.avatarUrl ?? undefined]));

  if (isLoading) {
    return (
      <div className="max-w-2xl mx-auto p-4 md:p-6 space-y-4">
        {[1, 2, 3].map((i) => (
          <Skeleton key={i} className="h-24 w-full" />
        ))}
      </div>
    );
  }

  if (!stats) return null;

  return (
    <PageTransition>
      <div className="max-w-2xl mx-auto p-4 md:p-6 space-y-8">
        <section>
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-2xl font-display font-bold flex items-center gap-2">
              <Trophy size={24} className="text-primary" />
              Leaderboard
            </h1>
            <Link to="/records" className="text-xs text-primary hover:underline">
              All-time records →
            </Link>
          </div>
          {stats.leaderboard.length === 0 ? (
            <div className="text-center py-16 text-muted-foreground">
              <Dices size={40} className="mx-auto mb-3 opacity-40" />
              <p>No games played yet.</p>
            </div>
          ) : (
            <>
              {stats.leaderboard.length >= 2 && (
                <div className="flex items-end justify-center gap-3 mb-8">
                  {stats.leaderboard[1] && (
                    <PodiumSlot entry={stats.leaderboard[1]} rank={2} avatarMap={avatarMap} />
                  )}
                  <PodiumSlot
                    entry={stats.leaderboard[0]}
                    rank={1}
                    featured
                    avatarMap={avatarMap}
                  />
                  {stats.leaderboard[2] && (
                    <PodiumSlot entry={stats.leaderboard[2]} rank={3} avatarMap={avatarMap} />
                  )}
                </div>
              )}
              <LeaderboardTable
                entries={stats.leaderboard}
                streaks={stats.streaks}
                avatarMap={avatarMap}
              />
            </>
          )}
        </section>

        {stats.mostPlayed && (
          <section>
            <h2 className="text-lg font-display font-semibold mb-3">Most Played</h2>
            <div className="flex items-center gap-3 p-4 rounded-lg border bg-card">
              <Dices size={20} className="text-primary shrink-0" />
              <div>
                <p className="font-semibold">{stats.mostPlayed.gameName}</p>
                <p className="text-sm text-muted-foreground">
                  {stats.mostPlayed.count} session{stats.mostPlayed.count !== 1 ? "s" : ""}
                </p>
              </div>
            </div>
          </section>
        )}

        {stats.streaks.length > 0 && (
          <section>
            <h2 className="text-lg font-display font-semibold mb-3">Win Streaks</h2>
            <div className="space-y-2">
              {stats.streaks.map((s) => (
                <div
                  key={s.playerId}
                  className="flex items-center justify-between p-3 rounded-lg bg-card border text-sm"
                >
                  <span className="flex items-center gap-2 font-medium">
                    {s.current > 0 && <Flame size={14} className="text-orange-400 shrink-0" />}
                    {s.name}
                  </span>
                  <span className="text-muted-foreground shrink-0 ml-2">
                    {s.current > 0 ? (
                      <span className="text-orange-400 font-bold">{s.current} active</span>
                    ) : (
                      <span className="text-muted-foreground">None active</span>
                    )}
                    {" · "}Best: <span className="text-foreground font-medium">{s.best}</span>
                  </span>
                </div>
              ))}
            </div>
          </section>
        )}

        {stats.headToHead.length > 0 && (
          <section>
            <h2 className="text-lg font-display font-semibold mb-3">Head to Head</h2>
            <HeadToHead entries={stats.headToHead} />
          </section>
        )}

        <section>
          <h2 className="text-lg font-display font-semibold mb-3">Win Rate Race</h2>
          <div className="bg-card rounded-lg border p-4">
            <WinRaceChart results={results} />
          </div>
        </section>

        <section>
          <h2 className="text-lg font-display font-semibold mb-3">Games per Month</h2>
          <MonthlyChart data={stats.perMonth} />
        </section>

        {stats.gameStats && stats.gameStats.length > 0 && (
          <section>
            <h2 className="text-lg font-display font-semibold mb-3">By Game</h2>
            <div className="space-y-2">
              {stats.gameStats.map((gs) => (
                <GameStatCard key={gs.gameId} gs={gs} />
              ))}
            </div>
          </section>
        )}
      </div>
    </PageTransition>
  );
}
