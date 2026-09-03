import { BookOpen, ClipboardList, Dices, FileText, Github, Star, Trophy } from "lucide-react";
import { motion } from "motion/react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Skeleton } from "../components/ui/skeleton";
import { useRecommended } from "../hooks/useRecommended";
import { usePublicSettings } from "../hooks/useSettings";

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

export default function LandingPage() {
  const [scrolled, setScrolled] = useState(false);
  const { data: recs = [], isLoading } = useRecommended();
  const { data: publicSettings } = usePublicSettings();
  const displayName = publicSettings?.displayName ?? "MC GamerTime";

  useEffect(() => {
    document.title = displayName;
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, [displayName]);

  const featured = recs.slice(0, 4);
  // Recommendations are a public endpoint only when PUBLIC_RECOMMENDED_ENABLED
  // is set, which is not the self-hosted default. Without it the query 401s and
  // the whole section — heading, "View all" and the hero anchor pointing at it —
  // has nothing to show.
  const hasPicks = isLoading || featured.length > 0;

  return (
    <div className="min-h-screen bg-background">
      {/* ── Header ── */}
      <header
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
          scrolled ? "bg-card/80 backdrop-blur-sm border-b" : "bg-transparent"
        }`}
      >
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Dices size={22} className="text-primary" />
            <span className="font-display font-bold text-lg text-primary">{displayName}</span>
          </div>
          <Button asChild size="sm">
            <Link to="/login">Sign in →</Link>
          </Button>
        </div>
      </header>

      {/* ── Hero ── */}
      <section
        className="min-h-[85vh] flex items-center relative overflow-hidden"
        style={{
          background: `
            radial-gradient(ellipse 80% 60% at 10% 40%, hsl(var(--primary) / 0.12) 0%, transparent 60%),
            radial-gradient(ellipse 50% 40% at 85% 65%, hsl(var(--primary) / 0.07) 0%, transparent 50%)
          `,
        }}
      >
        <div className="max-w-6xl mx-auto px-6 pt-16 w-full grid md:grid-cols-[3fr_2fr] gap-12 items-center">
          {/* Left: text */}
          <div className="space-y-6">
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="text-primary text-sm font-bold tracking-widest uppercase"
            >
              {displayName}
            </motion.p>
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="text-5xl md:text-7xl font-display font-bold leading-tight"
            >
              Board game tracking
            </motion.h1>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="text-lg text-muted-foreground max-w-md leading-relaxed"
            >
              Personal board game tracker.
            </motion.p>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
              className="flex flex-wrap items-center gap-4"
            >
              <Button asChild size="lg">
                <Link to="/login">Sign in →</Link>
              </Button>
              {hasPicks && (
                <a
                  href="#picks"
                  className="inline-flex items-center gap-2 text-primary font-medium hover:opacity-80 transition-opacity"
                >
                  See our picks ↓
                </a>
              )}
            </motion.div>
          </div>

          {/* Right: decorative shapes (desktop only) */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="hidden md:flex items-center justify-center relative h-80"
          >
            <div
              className="absolute w-52 h-52 rounded-2xl rotate-12"
              style={{
                border: "2px solid hsl(var(--primary) / 0.3)",
                backgroundColor: "hsl(var(--primary) / 0.05)",
              }}
            />
            <div
              className="absolute w-40 h-40 rounded-2xl"
              style={{
                transform: "translateX(3.5rem) translateY(2rem) rotate(-8deg)",
                border: "1px solid hsl(var(--primary) / 0.2)",
                backgroundColor: "hsl(var(--primary) / 0.08)",
              }}
            />
            <div
              className="absolute w-32 h-32 rounded-xl"
              style={{
                transform: "translateX(-2.5rem) translateY(3rem) rotate(3deg)",
                border: "2px solid hsl(var(--primary) / 0.25)",
                backgroundColor: "hsl(var(--primary) / 0.06)",
              }}
            />
            <Dices size={52} className="relative text-primary opacity-50" />
          </motion.div>
        </div>
      </section>

      {/* ── Feature Strip ── */}
      <div className="max-w-6xl mx-auto px-6 py-6 space-y-3">
        <p className="text-center text-xs font-semibold uppercase tracking-widest text-muted-foreground/60">
          Features
        </p>
        <div className="flex flex-wrap justify-center gap-x-8 gap-y-3">
          {[
            { icon: ClipboardList, label: "Track Game Sessions" },
            { icon: Trophy, label: "Leaderboard" },
            { icon: BookOpen, label: "Game Catalog" },
            { icon: Star, label: "Recommendations" },
            { icon: FileText, label: "Blog" },
          ].map(({ icon: Icon, label }) => (
            <span key={label} className="flex items-center gap-2 text-sm text-muted-foreground">
              <Icon size={15} aria-hidden={true} />
              {label}
            </span>
          ))}
        </div>
      </div>

      {/* ── Games Teaser ── */}
      {hasPicks && (
        <section id="picks" className="max-w-6xl mx-auto px-6 py-16 space-y-8">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-2xl font-display font-bold">Our recommendations</h2>
              <p className="text-sm text-muted-foreground mt-1">Some of our personal favorites</p>
            </div>
            <Link to="/recommended" className="text-sm text-primary font-medium hover:opacity-80">
              View all →
            </Link>
          </div>

          {isLoading ? (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="rounded-xl border bg-card overflow-hidden">
                  <Skeleton className="w-full aspect-[3/4]" />
                  <div className="p-3 space-y-2">
                    <Skeleton className="h-5 w-3/4" />
                    <Skeleton className="h-4 w-1/2" />
                  </div>
                </div>
              ))}
            </div>
          ) : featured.length > 0 ? (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {featured.map((r, i) => {
                const color = COLORS[r.gameName.charCodeAt(0) % COLORS.length];
                const sharedClass =
                  "rounded-xl border bg-card overflow-hidden transition-all hover:border-primary/40 hover:shadow-md";

                const cardContent = (
                  <motion.div
                    initial={{ opacity: 0, y: 16 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.4, delay: i * 0.08 }}
                  >
                    {r.imageUrl ? (
                      <img
                        src={r.imageUrl}
                        alt={r.gameName}
                        className="w-full aspect-[3/4] object-contain bg-muted"
                      />
                    ) : (
                      <div
                        className="w-full aspect-[3/4] flex items-center justify-center text-4xl font-display font-bold text-white"
                        style={{ backgroundColor: color }}
                      >
                        {r.gameName[0]?.toUpperCase() ?? "?"}
                      </div>
                    )}
                    <div className="p-3 space-y-1">
                      <p className="font-display font-bold text-sm leading-tight">{r.gameName}</p>
                    </div>
                  </motion.div>
                );

                return r.hasPost ? (
                  <Link key={r.pk} to={`/recommended/${r.slug ?? r.pk}`} className={sharedClass}>
                    {cardContent}
                  </Link>
                ) : (
                  <div key={r.pk} className={sharedClass}>
                    {cardContent}
                  </div>
                );
              })}
            </div>
          ) : null}
        </section>
      )}

      {/* ── Footer Strip ── */}
      <footer className="border-t bg-card/40">
        <div className="max-w-6xl mx-auto px-6 py-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <Button asChild size="sm" variant="outline">
            <Link to="/login">Sign in →</Link>
          </Button>
          <div className="flex items-center gap-3">
            <Link
              to="/privacy"
              className="text-base text-muted-foreground/50 hover:text-muted-foreground/80 transition-colors"
            >
              Privacy
            </Link>
            <a
              href="https://links.strandgaard.dev"
              className="text-base text-muted-foreground/50 hover:text-muted-foreground/80 transition-colors"
            >
              created by Magnus Strandgaard
            </a>
            <a
              href="https://github.com/strandgaard96"
              target="_blank"
              rel="noopener noreferrer"
              className="opacity-40 hover:opacity-80 transition-opacity"
              title="GitHub"
              aria-label="GitHub"
            >
              <Github className="w-7 h-7" aria-hidden="true" />
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
