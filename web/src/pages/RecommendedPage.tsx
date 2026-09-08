import { Dices } from "lucide-react";
import { motion } from "motion/react";
import { useEffect } from "react";
import { Link } from "react-router-dom";
import { PageTransition } from "../components/PageTransition";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Skeleton } from "../components/ui/skeleton";
import { useRecommended } from "../hooks/useRecommended";
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

function GameImagePlaceholder({ name, className = "" }: { name: string; className?: string }) {
  const color = COLORS[name.charCodeAt(0) % COLORS.length];
  return (
    <div
      className={`flex items-center justify-center font-display font-bold text-white ${className}`}
      style={{ backgroundColor: color }}
    >
      <span className="text-5xl">{name[0]?.toUpperCase() ?? "?"}</span>
    </div>
  );
}

export default function RecommendedPage() {
  const { data: recs = [], isLoading } = useRecommended();
  const { user } = useAuth();

  useEffect(() => {
    document.title = "MC GamerTime — Recommended Games";
    return () => {
      document.title = "MC GamerTime";
    };
  }, []);

  return (
    <PageTransition>
      <div className="min-h-screen bg-background">
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

        <main className="max-w-5xl mx-auto px-4 md:px-6 py-12 space-y-12">
          <motion.section
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="text-center space-y-3"
          >
            <h1 className="text-4xl font-display font-bold">Recommended games</h1>
            <p className="text-muted-foreground text-lg max-w-xl mx-auto">
              These are our favourite games.
            </p>
          </motion.section>

          {isLoading ? (
            <div className="space-y-6">
              <Skeleton className="w-full h-56 rounded-xl" />
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="rounded-lg border bg-card overflow-hidden">
                    <Skeleton className="w-full aspect-[3/4]" />
                    <div className="p-4 space-y-2">
                      <Skeleton className="h-6 w-3/4" />
                      <Skeleton className="h-4 w-1/3" />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : recs.length === 0 ? (
            <p className="text-muted-foreground text-center py-16">No recommendations yet.</p>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {recs.map((r, i) => {
                const cardContent = (
                  <motion.div
                    initial={{ opacity: 0, y: 16 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.4, delay: i * 0.06 }}
                    className="bg-card overflow-hidden h-full"
                  >
                    {r.imageUrl ? (
                      <img
                        src={r.imageUrl}
                        alt={r.gameName}
                        className="w-full aspect-[3/4] object-contain bg-muted"
                      />
                    ) : (
                      <GameImagePlaceholder name={r.gameName} className="w-full aspect-[3/4]" />
                    )}
                    <div className="p-4 space-y-2">
                      <h3 className="font-display font-bold text-lg leading-tight">{r.gameName}</h3>
                      {r.tags.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {r.tags.map((tag) => (
                            <Badge key={tag} variant="outline" className="text-xs">
                              {tag}
                            </Badge>
                          ))}
                        </div>
                      )}
                      <p className="text-sm text-muted-foreground leading-relaxed">{r.blurb}</p>
                      {r.hasPost && (
                        <p className="text-xs text-primary font-medium mt-1">Read more →</p>
                      )}
                    </div>
                  </motion.div>
                );
                return r.hasPost ? (
                  <Link
                    key={r.pk}
                    to={`/recommended/${r.slug ?? r.pk}`}
                    className="block border rounded-lg overflow-hidden hover:border-primary/40 hover:shadow-md transition-all"
                  >
                    {cardContent}
                  </Link>
                ) : (
                  <div key={r.pk} className="border rounded-lg overflow-hidden">
                    {cardContent}
                  </div>
                );
              })}
            </div>
          )}
        </main>
      </div>
    </PageTransition>
  );
}
