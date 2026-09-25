import { BookOpen, Dices } from "lucide-react";
import { GithubIcon } from "../components/ui/github-icon";
import { MotionConfig, motion, useMotionValueEvent, useScroll } from "motion/react";
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

const REPO_URL = "https://github.com/Strandgaard96/mc-gamertime";
const DOCS_URL = "https://mcgamertime-docs.drmaggi.com/self-hosting/quickstart/";

const INSTALL = `curl -fsSLO https://raw.githubusercontent.com/Strandgaard96/mc-gamertime/main/docker-compose.yml
printf 'ADMIN_USERNAME=admin\\nADMIN_PASSWORD=<your-password>\\n' > .env
docker compose up -d`;

const STACK = [
  { label: "Frontend", value: "React, TypeScript, Tailwind, TanStack Query" },
  { label: "API", value: "FastAPI on Python, SQLite or DynamoDB" },
  { label: "Runs on", value: "One Docker container, or AWS Lambda via Terraform" },
  { label: "Quality", value: "CI, 90% coverage floor, OpenSSF Scorecard" },
];

// Screenshots in public/landing/ come from a throwaway instance seeded with
// fictional players, never from a real group's data.
function Screenshot({
  src,
  alt,
  width,
  height,
  priority = false,
}: {
  src: string;
  alt: string;
  width: number;
  height: number;
  priority?: boolean;
}) {
  return (
    <img
      src={src}
      alt={alt}
      width={width}
      height={height}
      loading={priority ? "eager" : "lazy"}
      fetchPriority={priority ? "high" : "auto"}
      className="w-full h-auto rounded-xl border bg-card shadow-2xl shadow-primary/5"
    />
  );
}

const reveal = {
  initial: { opacity: 0, y: 24 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, amount: 0.3 },
  transition: { duration: 0.6, ease: [0.16, 1, 0.3, 1] as const },
};

export default function LandingPage() {
  const [scrolled, setScrolled] = useState(false);
  const { scrollY } = useScroll();
  useMotionValueEvent(scrollY, "change", (y) => setScrolled(y > 20));
  const { data: recs = [], isLoading } = useRecommended();
  const { data: publicSettings } = usePublicSettings();
  const displayName = publicSettings?.displayName ?? "MC GamerTime";
  const showProjectInfo = publicSettings?.showProjectInfo ?? false;

  useEffect(() => {
    document.title = displayName;
  }, [displayName]);

  const featured = recs.slice(0, 4);
  // Recommendations are a public endpoint only when PUBLIC_RECOMMENDED_ENABLED
  // is set, which is not the self-hosted default. Without it the query 401s and
  // the section has nothing to show.
  const hasPicks = isLoading || featured.length > 0;

  return (
    <MotionConfig reducedMotion="user">
      <div className="min-h-[100dvh] bg-background overflow-x-hidden">
        {/* ── Header ── */}
        <header
          className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
            scrolled ? "bg-card/80 backdrop-blur-xs border-b" : "bg-transparent"
          }`}
        >
          <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Dices size={22} className="text-primary" />
              <span className="font-display font-bold text-lg text-primary">{displayName}</span>
            </div>
            <Button asChild size="sm">
              <Link to="/login">Sign in</Link>
            </Button>
          </div>
        </header>

        {/* ── Hero ── */}
        <section
          className="relative"
          style={{
            background:
              "radial-gradient(ellipse 70% 55% at 75% 45%, hsl(var(--primary) / 0.10) 0%, transparent 65%)",
          }}
        >
          <div className="max-w-6xl mx-auto px-4 sm:px-6 pt-28 pb-12 md:pt-32 md:pb-16 grid md:grid-cols-[5fr_7fr] gap-10 md:gap-12 items-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
              className="space-y-6"
            >
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-display font-bold tracking-tight leading-[1.05]">
                Who won game night? Now there's proof.
              </h1>
              <p className="text-lg text-muted-foreground max-w-[42ch] leading-relaxed">
                Log every session, crown champions, and settle rivalries with stats your group can't
                argue with.
              </p>
              <div className="flex flex-wrap items-center gap-3">
                <Button asChild size="lg">
                  <Link to="/login">Sign in</Link>
                </Button>
                {showProjectInfo && (
                  <Button asChild size="lg" variant="outline">
                    <a href="#self-host">Self-host it</a>
                  </Button>
                )}
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 32, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              transition={{ duration: 0.8, delay: 0.15, ease: [0.16, 1, 0.3, 1] }}
            >
              <Screenshot
                src="/landing/leaderboard.webp"
                alt="Leaderboard with a podium for the top three players and a ranked table of ratings, wins and win rates"
                width={1600}
                height={1200}
                priority
              />
            </motion.div>
          </div>
        </section>

        {/* ── Showcase ── */}
        <section className="max-w-6xl mx-auto px-4 sm:px-6 pt-12 pb-16 md:pt-16 md:pb-24 space-y-10">
          <motion.div {...reveal} className="space-y-3">
            <h2 className="text-3xl md:text-4xl font-display font-bold tracking-tight">
              Every game night, remembered
            </h2>
            <p className="text-muted-foreground max-w-[60ch] leading-relaxed">
              Also inside: a game catalog with BoardGameGeek import, a picker for when nobody can
              decide, achievements, and a group blog.
            </p>
          </motion.div>

          <div className="grid gap-6 md:grid-cols-2 items-start">
            <motion.figure {...reveal} className="md:row-span-2 space-y-3">
              <Screenshot
                src="/landing/profile.webp"
                alt="Player profile showing games played, wins, win rate, streaks, nemesis and favourite prey"
                width={1600}
                height={2200}
              />
              <figcaption className="text-sm text-muted-foreground">
                <span className="text-foreground font-medium">Player profiles.</span> Streaks,
                favourite games, and the nemesis who keeps beating you.
              </figcaption>
            </motion.figure>
            <motion.figure {...reveal} className="space-y-3">
              <Screenshot
                src="/landing/home.webp"
                alt="Home dashboard with weekly stats, recent sessions and current standings"
                width={2000}
                height={1080}
              />
              <figcaption className="text-sm text-muted-foreground">
                <span className="text-foreground font-medium">Home.</span> Recent sessions and
                standings the moment you sign in.
              </figcaption>
            </motion.figure>
            <motion.figure {...reveal} className="space-y-3">
              <Screenshot
                src="/landing/records.webp"
                alt="All-time records page with total sessions, most played game and most active month"
                width={1600}
                height={1080}
              />
              <figcaption className="text-sm text-muted-foreground">
                <span className="text-foreground font-medium">All-time records.</span> Longest
                streaks, busiest months, and the reigning champion.
              </figcaption>
            </motion.figure>
          </div>
        </section>

        {/* ── Recommendations ── */}
        {hasPicks && (
          <section id="picks" className="max-w-6xl mx-auto px-4 sm:px-6 py-16 space-y-8">
            <div className="flex items-end justify-between gap-4">
              <div>
                <h2 className="text-2xl font-display font-bold">Our recommendations</h2>
                <p className="text-sm text-muted-foreground mt-1">Some of our personal favorites</p>
              </div>
              <Link
                to="/recommended"
                className="text-sm text-primary font-medium hover:opacity-80 shrink-0"
              >
                View all
              </Link>
            </div>

            {isLoading ? (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="rounded-xl border bg-card overflow-hidden">
                    <Skeleton className="w-full aspect-3/4" />
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
                          className="w-full aspect-3/4 object-contain bg-muted"
                        />
                      ) : (
                        <div
                          className="w-full aspect-3/4 flex items-center justify-center text-4xl font-display font-bold text-white"
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

        {/* ── Self-host (opt-in via Settings → Landing Page) ── */}
        {showProjectInfo && (
          <section id="self-host" className="scroll-mt-20 border-y bg-card/40">
            <div className="max-w-6xl mx-auto px-4 sm:px-6 py-16 md:py-24 grid gap-10 md:grid-cols-[7fr_5fr] md:gap-16">
              <motion.div {...reveal} className="space-y-6 min-w-0">
                <div className="space-y-3">
                  <h2 className="text-3xl md:text-4xl font-display font-bold tracking-tight">
                    Run your own
                  </h2>
                  <p className="text-muted-foreground max-w-[55ch] leading-relaxed">
                    Open source under MIT. One container, one SQLite file, no cloud account needed.
                  </p>
                </div>
                <div className="flex flex-wrap gap-3">
                  <Button asChild>
                    <a href={DOCS_URL} target="_blank" rel="noopener noreferrer">
                      <BookOpen size={16} className="mr-2" aria-hidden="true" />
                      Read the docs
                    </a>
                  </Button>
                  <Button asChild variant="outline">
                    <a href={REPO_URL} target="_blank" rel="noopener noreferrer">
                      <GithubIcon className="w-4 h-4 mr-2" aria-hidden="true" />
                      View source
                    </a>
                  </Button>
                </div>
              </motion.div>

              <motion.dl {...reveal} className="grid gap-6 content-start">
                {STACK.map(({ label, value }) => (
                  <div key={label} className="space-y-1">
                    <dt className="text-sm text-muted-foreground">{label}</dt>
                    <dd className="font-medium">{value}</dd>
                  </div>
                ))}
              </motion.dl>

              <motion.pre
                {...reveal}
                className="md:col-span-2 rounded-xl border bg-background p-4 text-sm leading-relaxed overflow-x-auto"
              >
                <code>{INSTALL}</code>
              </motion.pre>
            </div>
          </section>
        )}

        {/* ── Footer ── */}
        <footer className={showProjectInfo ? "" : "border-t"}>
          <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8 flex flex-col sm:flex-row items-center justify-between gap-4">
            <span className="font-display font-bold text-muted-foreground">{displayName}</span>
            <div className="flex items-center gap-5 text-sm text-muted-foreground">
              <Link to="/privacy" className="hover:text-foreground transition-colors">
                Privacy
              </Link>
              <a
                href={REPO_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 hover:text-foreground transition-colors"
              >
                <GithubIcon className="w-4 h-4" aria-hidden="true" />
                Source
              </a>
            </div>
          </div>
        </footer>
      </div>
    </MotionConfig>
  );
}
