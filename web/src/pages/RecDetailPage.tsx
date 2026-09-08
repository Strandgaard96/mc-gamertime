import { ChevronLeft, Dices } from "lucide-react";
import { useEffect } from "react";
import { Link, useParams } from "react-router-dom";
import { PageTransition } from "../components/PageTransition";
import { SafeHtml } from "../components/SafeHtml";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Skeleton } from "../components/ui/skeleton";
import { useRecommendedDetail } from "../hooks/useRecommended";
import { useAuth } from "../lib/AuthContext";

const COLORS = [
  "#e11d48",
  "#7c3aed",
  "#2563eb",
  "#0891b2",
  "#059669",
  "#d97706",
  "#c2410c",
  "#be185d",
];

function WeightDots({ weight }: { weight: number }) {
  const filled = Math.round(weight);
  return (
    <span className="flex gap-0.5">
      {Array.from({ length: 5 }, (_, i) => (
        <span
          key={i}
          className={`text-base leading-none ${i < filled ? "text-primary" : "text-muted-foreground/30"}`}
        >
          ●
        </span>
      ))}
    </span>
  );
}

export default function RecDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data: rec, isLoading } = useRecommendedDetail(id);
  const { user } = useAuth();

  useEffect(() => {
    if (rec) document.title = `MC GamerTime — ${rec.gameName}`;
    return () => {
      document.title = "MC GamerTime";
    };
  }, [rec?.gameName, rec]);

  const color = rec ? COLORS[rec.gameName.charCodeAt(0) % COLORS.length] : "#7c3aed";

  return (
    <PageTransition>
      <div className="min-h-screen bg-background flex flex-col">
        {!user && (
          <header className="border-b bg-card/60 backdrop-blur-sm sticky top-0 z-10">
            <div className="max-w-5xl mx-auto px-4 md:px-6 h-14 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Dices size={20} className="text-primary" />
                <span className="font-display font-bold text-foreground">MC GamerTime</span>
              </div>
              <Button asChild size="sm">
                <Link to="/login">Sign in →</Link>
              </Button>
            </div>
          </header>
        )}

        <div className="flex-1 max-w-5xl w-full mx-auto px-4 md:px-6 py-6">
          <Link
            to="/recommended"
            className="text-sm text-muted-foreground hover:text-foreground flex items-center gap-1 w-fit"
          >
            <ChevronLeft size={16} />
            Recommended Games
          </Link>

          {isLoading ? (
            <div className="mt-6 space-y-4">
              <Skeleton className="w-full h-72 rounded-xl" />
              <Skeleton className="h-10 w-3/4" />
              <Skeleton className="h-4 w-1/2" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-48 w-full" />
            </div>
          ) : !rec ? (
            <p className="text-muted-foreground py-20 text-center mt-6">
              Recommendation not found.
            </p>
          ) : (
            <div className="mt-6 grid lg:grid-cols-[1fr_260px] gap-8 items-start">
              {/* ── Main content ── */}
              <div className="space-y-6">
                {rec.imageUrl ? (
                  <img
                    src={rec.imageUrl}
                    alt={rec.gameName}
                    className="w-full max-h-80 object-cover rounded-xl"
                  />
                ) : (
                  <div
                    className="w-full h-64 rounded-xl flex items-center justify-center text-8xl font-display font-bold text-white"
                    style={{ backgroundColor: color }}
                  >
                    {rec.gameName[0]?.toUpperCase() ?? "?"}
                  </div>
                )}

                <h1 className="text-3xl font-display font-bold">{rec.gameName}</h1>

                {/* Inline stats — mobile only */}
                <div className="lg:hidden flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-muted-foreground">
                  {(rec.minPlayers != null || rec.maxPlayers != null) && (
                    <span>
                      {rec.minPlayers === rec.maxPlayers
                        ? `${rec.minPlayers} players`
                        : `${rec.minPlayers ?? "?"}–${rec.maxPlayers ?? "?"} players`}
                    </span>
                  )}
                  {rec.playTime != null && <span>{rec.playTime} min</span>}
                  {rec.weight != null && (
                    <span className="flex items-center gap-1.5">
                      Complexity <WeightDots weight={rec.weight} />
                    </span>
                  )}
                  {rec.yearPublished != null && <span>{rec.yearPublished}</span>}
                </div>

                {/* Mobile tags */}
                {(rec.bestFor || rec.tags.length > 0) && (
                  <div className="lg:hidden flex flex-wrap gap-2">
                    {rec.bestFor && <Badge variant="secondary">Best with {rec.bestFor}</Badge>}
                    {rec.tags.map((tag) => (
                      <Badge key={tag} variant="outline" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                )}

                {/* Pull-quote blurb */}
                <blockquote className="border-l-4 border-primary/60 pl-4 italic text-muted-foreground text-base leading-relaxed">
                  {rec.blurb}
                </blockquote>

                {rec.content && (
                  <SafeHtml html={rec.content} className="prose prose-sm prose-invert max-w-none" />
                )}
              </div>

              {/* ── Sidebar — desktop only ── */}
              <aside className="hidden lg:block">
                <div className="sticky top-24 bg-card border rounded-xl p-5 space-y-5">
                  <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                    Game Details
                  </h3>

                  <div className="space-y-3 text-sm">
                    {(rec.minPlayers != null || rec.maxPlayers != null) && (
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Players</span>
                        <span>
                          {rec.minPlayers === rec.maxPlayers
                            ? rec.minPlayers
                            : `${rec.minPlayers ?? "?"}–${rec.maxPlayers ?? "?"}`}
                        </span>
                      </div>
                    )}
                    {rec.playTime != null && (
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Play time</span>
                        <span>{rec.playTime} min</span>
                      </div>
                    )}
                    {rec.weight != null && (
                      <div className="flex justify-between items-center">
                        <span className="text-muted-foreground">Complexity</span>
                        <WeightDots weight={rec.weight} />
                      </div>
                    )}
                    {rec.yearPublished != null && (
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Year</span>
                        <span>{rec.yearPublished}</span>
                      </div>
                    )}
                    {rec.bestFor && (
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Best with</span>
                        <span>{rec.bestFor}</span>
                      </div>
                    )}
                  </div>

                  {rec.tags.length > 0 && (
                    <div className="pt-4 border-t">
                      <div className="flex flex-wrap gap-1">
                        {rec.tags.map((tag) => (
                          <Badge key={tag} variant="outline" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </aside>
            </div>
          )}
        </div>

        {!user && rec && (
          <div className="sticky bottom-0 border-t bg-card/80 backdrop-blur-sm py-3">
            <div className="max-w-5xl mx-auto px-4 md:px-6 flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Track your own game nights</span>
              <Button asChild size="sm">
                <Link to="/login">Sign in →</Link>
              </Button>
            </div>
          </div>
        )}
      </div>
    </PageTransition>
  );
}
