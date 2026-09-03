# Changelog

## 1.0.0 (2026-09-03)


### Bug Fixes

* pin setup-uv to v10.0.1 and track .env.example ([39e9f39](https://github.com/Strandgaard96/mc-gamertime/commit/39e9f39e3484e9c8666749268fcece6ee2515547))
* rebuild docs when .env.example changes ([e4e4ed5](https://github.com/Strandgaard96/mc-gamertime/commit/e4e4ed570d27c9c1a6e288900ba656cdd93667d1))

## 1.7.2 (2026-08-28)


### Bug Fixes

* **web:** correct the product name in link previews and the PWA manifest
* **web:** use one spelling of "favourite" on the player profile

## 1.7.1 (2026-08-21)


### Bug Fixes

* **api:** tell caches not to store API responses
* **auth:** account lockout 500'd on the cloud deployment
* **auth:** guard the unknown-user timing hash against over-long passwords too
* **auth:** reject passwords over bcrypt's 72-byte limit instead of 500ing
* **auth:** set the session cookie's Secure flag from the request scheme
* **cloud:** require a session to read avatars and uploaded images
* **infra:** stop CloudFront serving DynamoDB exports from the web bucket


### Performance Improvements

* **media:** reuse images for 20 minutes, with cache-busted avatar URLs

## 1.7.0 (2026-08-20)


### Features

* make self-hosting the default deployment, AWS opt-in


### Bug Fixes

* **cors:** allow the CloudFront distribution domain as a browser origin
* **deps:** patch HIGH-severity CVEs in api and docs-site
* **docker:** apply Debian security updates in the image build
* **scripts:** list-users crashed on users created through the web UI

## 1.6.0 (2026-07-04)


### Features

* fail at startup when no users exist and admin vars unset
* fail at startup when no users exist and admin vars unset


### Bug Fixes

* auth security hardening — password bounds, bcrypt rounds, cookie attributes
* cap password field length at 1024 chars to prevent bcrypt DoS
* make bcrypt work factor explicit (rounds=12); document rate-limiter Lambda scope
* match delete_cookie attributes to set_cookie (secure, samesite=strict)
* raise minimum password length to 12 characters (NIST 800-63B)
* repair CI — stale bootstrap tests + docs Node version
* **security:** API & infrastructure hardening from audit
* **security:** authorization audit findings
* **security:** logging & monitoring audit findings
* **security:** session role re-check from cookie audit (S-2)
* use explicit bcrypt rounds=12 in admin bootstrap path

## 1.5.0 (2026-06-25)


### Features

* add appBaseUrl to AdminSettings type and API client
* add DB-backed appBaseUrl setting
* add Instance URL card to Settings page
* implement appBaseUrl validator (scheme required, trailing-slash stripped, empty clears)
* prefer DB appBaseUrl over env var for reset-link host


### Bug Fixes

* correct bgg_token setup instructions in AWS deploy guide
* document Instance URL setting, reject scheme-only appBaseUrl
* selfhost security hardening (reset-link spoofing + rate-limit collapse)
* sqlite_import.py accepts export-tables.py's boardsite-prefixed filenames
* trust forwarded client IP from private ranges so rate limiting survives a reverse proxy

## 1.4.1 (2026-06-21)


### Bug Fixes

* gate GHCR push on a Trivy scan inside publish.yml
* gate GHCR push on a Trivy scan inside publish.yml

## 1.4.0 (2026-06-21)


### Features

* add local trivy dependency scan to pre-commit
* add local trivy dependency scan to pre-commit


### Bug Fixes

* patch starlette and cryptography CVEs flagged by Trivy
* patch starlette and cryptography CVEs flagged by Trivy image scan

## 1.3.0 (2026-06-21)


### Features

* add frontend test infra and CI image vulnerability scanning
* add game image upload API call and shared upload hook
* add manual game entry mode to AddGameDialog
* add POST /api/games/upload for game cover images
* allow editing core game fields (name, image, players, etc.) for any game


### Bug Fixes

* allow clearing core game fields in the edit dialog
* allow game-images/ prefix in the selfhost storage proxy
* correct trivy-action tag (needs v prefix, bump to latest)
* origin guard fails open when ORIGIN_TOKEN is unset
* origin guard fails open when ORIGIN_TOKEN unset
* pin vitest to stable 3.x to fix npm ci in CI
* reset manual-entry image state when AddGameDialog closes

## 1.2.0 (2026-06-21)


### Features

* add automated backup script for selfhost with retention
* add forgot/reset-password pages and document SMTP config
* add forgot/reset-password routes and --email flag to user scripts
* add gated /metrics endpoint behind METRICS_ENABLED
* add GET/PUT settings API routes
* add interactive first-run wizard to create-user.py
* add password-reset token signing to lib/auth.py
* add prometheus_client metrics counters
* add settings API client functions and types
* add settings table for instance-level config
* add SettingsPage and usePublicSettings hook
* add SQLite schema migration framework
* add sqlite_export.py for selfhost table-level JSON export
* add sqlite_import.py with atomic validation for selfhost data import
* add stdlib SMTP mailer for selfhost password reset
* **api:** bootstrap self-host admin user from ADMIN_USERNAME/ADMIN_PASSWORD
* layer DB-backed BGG token override over env/SSM fallback
* make docker-compose.yml self-sufficient for selfhost
* move settings entry point from nav tab to header cog icon
* provision settings DynamoDB table in Terraform
* resolve BGG token through DB-override precedence at cold start
* self-host default admin bootstrap via ADMIN_USERNAME/ADMIN_PASSWORD
* self-host P3 — password reset, metrics endpoint, interactive wizard
* selfhost P0 data safety (backup automation, sqlite export/import)
* selfhost P2 maintainability (SQLite migrations, commit convention, recovery runbook)
* split settings page into independent branding and integrations cards
* wire Settings page into nav and replace hardcoded brand strings


### Bug Fixes

* **docs:** correct stale code refs and broken prose in docs-site
* install sqlite3 CLI in runtime image for disaster-recovery runbook
* narrow sqlite_export OperationalError handling to missing-table only
* rate-limit /reset-password to match /forgot-password
* show explanatory message on ResetPasswordPage when token is missing
* stop deriving password-reset link host from client-supplied Host header
* warn before live-DB export/import, verify backup tar contents

## 1.1.0 (2026-06-19)


### Features

* add DynamoTable semantic update methods (add_to_set, remove_from_set, increment_with_timestamp)
* add LocalFsClient for selfhost STORAGE_BACKEND=local
* add SQLite-backed table implementation for selfhost DB_BACKEND=sqlite
* collapse selfhost docker-compose to a single app container (SQLite + local fs)
* dispatch to LocalFsClient when STORAGE_BACKEND=local
* dispatch to SQLite backend when DB_BACKEND=sqlite
* register /storage router when STORAGE_BACKEND=local
* support STORAGE_BACKEND=local in upload-URL and storage-proxy 404 handling


### Bug Fixes

* **docs:** add missing PUID/PGID to .env.example template
* **docs:** port Backups and migration content into Backups & Upgrades page
* **docs:** remove leftover TODO placeholder from Features page
* **docs:** replace stale volume check with bind-mount permission check
* **docs:** restore all three archives in backups example, not just dynamodb
* **docs:** sync configuration page JWT_SECRET path to config/ bind mount
* **docs:** sync HTTPS page certificate storage path to config/ bind mount
* **docs:** unbreak MDX build, sync architecture page to config/ bind mounts
* reject path traversal in LocalFsClient keys

## 1.0.2 (2026-06-16)


### Bug Fixes

* fix url migration

## 1.0.1 (2026-06-16)


### Bug Fixes

* formatting and update pre-commit
* prevent query of players endpoint on homepage when not logged in

## 1.0.0 (2026-06-16)


### Features

* 12 UX/UI improvements across frontend
* add 5 dark themes to registry, remove parchment
* add achievement computation library with tests
* add Achievement, PlayerStats, GameStat types and getPlayerStats API function
* add AchievementBadge component
* add achievements, win rate trend chart, and per-game stats to player profiles
* add backend API documentation to handbook
* add By Game expandable section to Leaderboard page
* add CSS variable blocks for 5 new dark themes, remove parchment
* add DELETE /api/results/{pk} endpoint (admin only)
* add DELETE /api/users/{username} with self/last-admin guards
* add delete_user DB helper
* add deleteResult API fn and useDeleteResult hook
* add dice SVG favicon
* add edit-user dialog to UsersPage (display name, role, password)
* add escalating-delay brute-force protection to login
* add favorites-only toggle to CatalogFilters
* add field validators to recommended route (non-empty gamePk and blurb)
* add field validators to results route (non-empty, date format, score &gt;= 0)
* add frontend documentation to handbook
* add gameStats breakdown to compute_stats
* add GET /players/{id}/stats with achievements, per-game stats, win rate trend
* add infrastructure documentation to handbook
* add initial handbook structure and DynamoDB documentation
* add inline delete confirm and post link buttons to game log
* add lib/db package with per-entity DynamoDB modules
* add optional score field to log result dialog and display in session history
* add pressable tap-feedback utility, apply to Button
* add PUT /users/:username admin route for display-name/role/password updates
* add rec detail endpoint, hasPost, BGG metadata denormalization, content field
* add RecDetailPage with BGG metadata, rich content, and public access
* add RecEditorPage — full-screen Tiptap editor for rec posts
* add RecommendationDetail type, getRecommendedDetail API, useRecommendedDetail hook
* add slug to rec URLs (e.g. /recommended/catan)
* add subtitle to recommendations section on landing page
* add subtle feature strip to landing page
* add tap feedback to game cards, post cards, game list rows
* add tap feedback to mobile bottom nav tabs
* add tokenVersion claim for JWT session revocation
* add updateUser API function
* add useDraft localStorage hook for post draft recovery
* add usePlayerStats hook
* add user deletion to UsersPage UI
* add WinRateTrendChart component using Recharts
* admin result editing via PUT /api/results/{id}
* animated empty state for game catalog
* **api:** add /storage proxy for selfhost S3-compatible stores
* **api:** add comment create/delete endpoints
* **api:** add Elo rating computation
* **api:** add IP rate limiting (5/min) to POST /api/auth/login
* **api:** add make_s3_client() factory for selfhost S3-compatible stores
* **api:** add milestone detection to result POST response
* **api:** add notifications DynamoDB table and db layer
* **api:** add notifications list/read endpoints
* **api:** add ORIGIN_GUARD_ENABLED flag for selfhost (no CloudFront)
* **api:** add per-game player variable config + game edit endpoint
* **api:** add POST /api/reactions/toggle
* **api:** add PUBLIC_RECOMMENDED_ENABLED flag for selfhost
* **api:** add Pydantic request model to games route
* **api:** add Pydantic request model to users route
* **api:** add Pydantic request models to auth and players routes
* **api:** add Pydantic request models to posts route
* **api:** add Pydantic request models to recommended route
* **api:** add Pydantic request models to results route
* **api:** add reactions table and GET /api/reactions
* **api:** add recommended games CRUD with public GET endpoint
* **api:** add SECRETS_PROVIDER=env for selfhost secret config
* **api:** compute per-variable and per-seat win/pick rate stats
* **api:** detect and notify newly-earned achievements on result creation
* **api:** make achievements declarative via composable rules
* **api:** rank leaderboard by Elo rating
* **api:** serve SPA via STATIC_DIR and register /storage proxy for selfhost
* **api:** support DYNAMODB_ENDPOINT_URL for selfhost dynamodb-local
* **api:** validate per-player variables and seat order against game config
* **api:** validate player IDs and winnerId membership on result creation
* **api:** wire slowapi limiter into FastAPI app
* autosave blog post drafts to localStorage with restore banner
* block deletion of users referenced in results, clean up avatar
* bump tokenVersion on logout, add revoke-sessions ops script
* dashboard home page, sidebar nav, leaderboard podium
* delete lib/dynamo.py; clean up conftest to use FakeTable only
* detect and toast new achievements after logging a game result
* **docker:** add .env.example for selfhost S3 credentials
* **docker:** add Caddy reverse-proxy overlay for HTTPS (Tailscale/public/LAN)
* **docker:** add docker-compose.yml for selfhost stack (app + dynamodb-local + seaweedfs)
* **docker:** add multi-stage selfhost Dockerfile (web build + api runtime)
* **docker:** add SeaweedFS S3 identity config template (single identity, no anonymous)
* **docker:** add selfhost entrypoint (JWT secret + table/bucket bootstrap)
* **docker:** add setup.sh to generate .env and render SeaweedFS config
* **docs:** add architecture page with container diagram and volumes table
* **docs:** add cloud deploy and contributing sections
* **docs:** add Features card to landing page
* **docs:** add features page
* **docs:** add landing page and self-hosting section
* **docs:** add sidebar ordering and GHCR quickstart tip
* **docs:** add site URL, sitemap, and Mermaid CDN
* **docs:** scaffold Astro Starlight docs-site
* edit button and mood display on session cards
* editorial featured card layout for RecommendedPage
* editorial sidebar and pull-quote blurb for RecDetailPage
* emoji picker in post editor toolbar
* enable DynamoDB PITR and deletion protection on all tables
* enable S3 versioning and 90-day lifecycle on blog images
* fix idFromPk for clean IDs, update Player type, remove addPlayer
* health endpoint + backend-down detection at login
* hero header card for PlayerProfilePage
* implement public landing page with hero and game teaser
* **infra:** add boardsite-reactions DynamoDB table
* **infra:** add IP-allowlist WAF for dev CloudFront distribution
* make rec cards clickable when hasPost, add Write/Edit Post buttons to admin
* manual DynamoDB table export script
* migrate routes/auth to lib.db.users
* migrate routes/games to lib.db.games; clean pk (no GAME# prefix)
* migrate routes/players; remove create_player; list returns public user info
* migrate routes/posts to lib.db.posts; clean pk (no POST# prefix)
* migrate routes/recommended to lib.db.recs + lib.db.games; clean pk
* migrate routes/results to lib.db; validate players via lib.db.users; clean pk
* migrate routes/stats to lib.db.results
* migrate routes/users to lib.db.users; clean item shape
* mood selector and edit mode in LogResultDialog
* optional mood (1-5) on results
* per-game average/high score stats and best-score badge
* per-player average score trend chart
* Perfect 10 score achievement
* pre-select session in post editor from ?session URL param
* publish Docker image to GHCR on push to main and version tags
* remove per-player score from log card avatar row
* route / to LandingPage for unauthenticated users
* **scripts:** add create-user.py to bootstrap users in DynamoDB
* **scripts:** add delete-user.py to remove users from DynamoDB
* **scripts:** add idempotent DynamoDB Local table bootstrap for selfhost
* **scripts:** add idempotent S3 bucket bootstrap for selfhost
* **scripts:** respect DYNAMODB_ENDPOINT_URL in user-management scripts
* self-host Space Grotesk via [@fontsource](https://github.com/fontsource) — remove Google Fonts CDN
* **selfhost:** replace caddy named volumes with config/ bind mounts
* **selfhost:** replace named volumes with config/ bind mounts
* show session-expired toast and redirect back after re-login
* skip Lambda build when api/ source unchanged
* styled numbered rank badges in LeaderboardTable
* update landing page hero subtitle copy
* validate game existence when creating result
* **web:** add admin dialog to configure per-game player variables and turn order
* **web:** add AdminRecommendedPage with CRUD management and routing
* **web:** add asChild prop to Button for rendering as a single link element
* **web:** add Avatar component with deterministic initials colors
* **web:** add Avatar, Lucide stat icons, and font-display to detail pages
* **web:** add ChevronLeft back icon and font-display to post pages
* **web:** add Lucide icons, font-display headings, and empty state polish to pages
* **web:** add Lucide icons, hover effects, and image gradient to game cards
* **web:** add MC GameTime branding, theme picker, Lucide nav icons, Sonner toaster
* **web:** add medals, win rate bars, avatars, and streak flames to leaderboard
* **web:** add notification bell to header nav
* **web:** add notifications API client and hook
* **web:** add page slide transitions via Framer Motion AnimatePresence
* **web:** add PageTransition component and install framer-motion + canvas-confetti
* **web:** add Player Wrapped recap to profile page
* **web:** add public /recommended landing page with game cards
* **web:** add PWA icon assets and generation script
* **web:** add PWA manifest, service worker, and iOS meta tags
* **web:** add reactions and comments to session cards
* **web:** add reactions/comments API client and hooks
* **web:** add Recommendation type, API functions, and useRecommended hook
* **web:** add stagger animations, win rate bars, and stat counters
* **web:** add theme system, dark-gold/midnight palettes, Space Grotesk font
* **web:** add toast notifications to all mutation hooks
* **web:** add types for player variables, seat tracking, and variable/seat stats
* **web:** add updateGame API client and useUpdateGame hook
* **web:** add WrappedOverlay slideshow component
* **web:** collect player variables and seat order in LogResultDialog
* **web:** confetti burst + milestone toast on game log
* **web:** render achievement icons from the backend def
* **web:** replace window.location.href auth redirects with navigation singleton
* **web:** respect safe-area insets in standalone PWA mode
* **web:** show Elo rating column on leaderboard
* **web:** show per-variable and per-seat win/pick rates on game stat cards
* **web:** show update toast when new service worker is available
* **web:** sync theme-color meta to active theme


### Bug Fixes

* 5 audit quick-wins — nav picks, upload toast, favorite await, list-view log button, game-detail log entry
* add 14-day noncurrent expiry for Vite assets and abort incomplete multipart uploads
* add aria-hidden to decorative feature strip icons
* Add auth fix for lambda startup
* add blurb validator to UpdateRecommendedBody to prevent whitespace updates
* add CloudFront security response headers policy (HSTS, X-Frame-Options, X-Content-Type-Options)
* add Features label above feature strip
* add missing defusedxml pin to requirements.txt (prod 500s on every route)
* add paginated_scan helper; replace all unbounded scan() calls
* add target and rel to external links in privacy policy
* add zero-guard to dominant achievement division
* address code review findings from UX improvement batch
* allow clearing optional fields via explicit null in rec/post updates
* allowlist content types on image upload endpoint
* **api:** apply prefix allowlist to /storage PUT (security review finding)
* **api:** centralize object base URL for selfhost display + upload URLs
* **api:** generalize /storage PUT into an authenticated upload sink
* **api:** replace deprecated datetime.utcnow() with datetime.now(timezone.utc)
* **api:** strip favorites from game PUT response, normalize null playerVariables
* atomic failed-login counter increment
* avatar size cap, constant-time origin compare, pin upload extension
* build lambda.zip for Python 3.12 manylinux (fixes pydantic_core import error)
* bump tokenVersion on role/password update; reject empty displayName/password
* constrain score input to range 1-10
* correct CloudFront response headers policy block names
* correct yearPublished camelCase label in CatalogFilters
* define _floats_to_decimal in db/base.py; apply float conversion in put_post and put_rec
* disable delete-user button while mutation pending
* **docker:** add .dockerignore, run as non-root, add healthcheck (code review findings)
* **docker:** add resource limits and security hardening (no-new-privileges, cap_drop)
* **docker:** drop dynamodb-local root via init container that pre-chowns the volume
* **docker:** fix healthcheck regressions — curl -s for dynamodb, nc for seaweedfs S3 port, revert image name
* **docker:** fix seaweedfs healthcheck false-positive, probe correct port, use canonical image name
* **docker:** pin image versions, add restart policies and healthcheck-based startup ordering
* **docker:** publish port 8080 in caddy overlay for LAN default option
* **docker:** selfhost smoke-test fixes (dynamodb-local volume perms, SeaweedFS bucket creation via filer API)
* **docs:** clarify base vs optional Caddy container in architecture intro
* emoji picker popup collapses to 0-width grid columns
* enforce score 1-10 server-side, close milestone scan race
* future-date slack for non-UTC users, block game delete with references
* gate autosave on draftToRestore; skip restore for empty drafts
* gate GameCard PenLine button behind admin role check
* guard self-demotion in edit-user dialog; toast on no-op submit
* guard winRate division in gameStats computation
* handle indented comments in requirements.txt parsing
* harden BGG client URL encoding and XML parsing
* increase web-assets lifecycle noncurrent expiry to 90 days to prevent blog image override
* **infra:** wire REACTIONS_TABLE env var into Lambda
* invalidate detail cache on recommendation update; invalidate playerStats on result delete
* lock down game-creation schema against mass assignment
* low-impact UX polish
* Make infrastructure domain independent on naming
* make Post.gamePk/sessionPk/gameName optional to match backend; guard PostCard crash
* polish and consistency across remaining pages
* reject negative scores client-side, document route-list invariant
* remove featured card treatment on RecommendedPage — all recs now uniform grid
* remove gratuitous get_user guard from get_player_stats
* remove models.py from build.sh (file no longer exists)
* remove phantom sk/type fields from Game type
* replace uv pip -t with --target for lambda build
* resolve tailwind-merge transition conflict in pressable
* return 404 when deleting non-existent game or recommendation
* revoke sessions on password change, validate result edit fields
* **scripts:** create-user.py respects USERS_TABLE/AWS_REGION env vars
* seed game in winner-not-in-players test to test correct validation
* **selfhost:** add necessary capabilities for bind mounts and update seaweedfs healthcheck
* show hover cue only on clickable rec cards
* show threshold placeholders when stats cards are absent
* skip auth spinner on public routes — landing page paints immediately
* skip malformed player entries in compute_stats
* surface 429 Retry-After on login lockout
* surface backend error messages in log-game and create-user toasts
* transparent favicon background
* typo in landing page heading; remove commented-out code
* update create-user for new schema; add list-users script and task commands
* use apiFetch for recommended endpoints to enable consistent 401 handling
* use clean white destructive-foreground, fix obsidian muted saturation
* use min-h-dvh to stabilise mobile bottom nav
* use object-contain on recommended page game images
* UX/UI improvements across catalog, results, and leaderboard
* validate non-empty title and content in CreatePostBody
* validate saved theme against THEMES before applying to DOM
* **web:** add inline player creation to LogResult dialog and player profile links to leaderboard and results
* **web:** avoid login-form flash for already-authenticated visitors
* **web:** correct outro slide copy on Wrapped overlay
* **web:** fix blog post body text invisible on dark themes
* **web:** getCurrentUser uses raw fetch to avoid 401 redirect on public pages
* **web:** link user rows to player profile page
* **web:** move desktop nav breakpoint to lg to prevent tablet overflow
* **web:** pluralize session count on home page
* **web:** preserve comment text on submit failure, label reaction picker
* **web:** prevent stale variable keys and game-switch state leakage in LogResultDialog
* **web:** remove duplicate count in HomePage session-logged text
* **web:** remove nested &lt;a&gt;&lt;button&gt; on LandingPage sign-in links
* **web:** remove nested &lt;a&gt;&lt;button&gt; on PostEditorPage cancel link
* **web:** remove nested &lt;a&gt;&lt;button&gt; on PostsPage new-post links
* **web:** remove nested &lt;a&gt;&lt;button&gt; on RecDetailPage sign-in links
* **web:** remove nested &lt;a&gt;&lt;button&gt; on RecommendedPage sign-in link
* **web:** scope WrappedOverlay keydown effect and improve a11y
* **web:** show Elo rating on records page champion card
* **web:** use registered users as players in LogResult, link nav username to profile
* WinRaceChart hidden-player tooltip, duplicate ticks, connectNulls bridge


### Reverts

* remove CloudFront response headers policy (not supported on free pricing plan)

## Changelog
