---
title: Architecture
description: How the frontend and backend fit together — entry points, auth flow, data layer, request flow.
sidebar:
  order: 3
---

A code-level walkthrough of the application. Start here when you want to understand how things connect or why something is happening.

---

## Entry Points

### Frontend: `web/src/main.tsx`

This is where React boots. It sets up three things that wrap the entire app:

1. **`BrowserRouter`** — enables React Router (URL-based navigation)
2. **`QueryClientProvider`** — TanStack Query cache with a 2-minute stale time. Every data fetch lives in this cache.
3. **`App`** and **`Toaster`** (sonner) — the app + global toast notifications

### Backend: `api/main.py`

FastAPI app created here. Every incoming request goes through this file.

**Critical: the `origin_guard` middleware.** Every request — before hitting any route — passes through it. It:
1. Calls an internal `_initialize()` on first request (cold start). This fetches three secrets from AWS SSM Parameter Store: JWT secret, origin token, BGG API token.
2. In production: checks that the `x-origin-token` header matches the SSM secret. This header is injected by CloudFront. Direct calls to API Gateway without it get a 403.
3. In dev (`DEV_MODE=true`): skips the token check entirely.

Routers are mounted at fixed prefixes:
```
/api/auth          → api/routes/auth.py
/api/games         → api/routes/games.py
/api/players       → api/routes/players.py
/api/posts         → api/routes/posts.py
/api/results       → api/routes/results.py
/api/recommended   → api/routes/recommended.py
/api/stats         → api/routes/stats.py
/api/users         → api/routes/users.py
/api/reactions     → api/routes/reactions.py
/api/comments      → api/routes/reactions.py (comments_router)
/api/notifications → api/routes/notifications.py
/api/settings      → api/routes/settings.py
/storage           → api/routes/storage.py (only mounted when STORAGE_BACKEND=local or S3_ENDPOINT_URL is set)
```

---

## Auth Flow — Login to Logged In

This is the most important flow to understand because everything depends on it.

### Step 1: App loads → checks if already logged in

`App.tsx` renders `<AuthProvider>` which immediately calls `getCurrentUser()` (`web/src/lib/api.ts`):

```
GET /api/auth/me
```

- Cookie `token` is sent automatically by the browser
- Backend (`api/routes/auth.py`): `require_auth` dependency reads the `token` cookie, decodes the JWT
- If valid: returns `{ sub, role, displayName }`
- If invalid/missing: returns 401 → `getCurrentUser` catches and returns `null`

The result lands in `AuthContext` as `user: AuthUser | null`. `loading` starts `true`, goes `false` when this resolves.

### Step 2: `AppShell` decides what to render

If `loading` is still true → shows a loading state. When loading finishes:

- `user === null` → renders the unauthenticated routes (login page, public recommended, 404 → redirect to login)
- `user !== null` → renders the full app with nav, all routes

### Step 3: Login form submits

`LoginPage` calls `login(username, password)` (`web/src/lib/api.ts`):

```
POST /api/auth/login
Body: { username, password }
```

Backend (`api/routes/auth.py`):
1. Looks up user in DynamoDB users table via `get_user(username)`
2. `bcrypt.checkpw()` checks password hash. **Timing attack protection**: if user not found, still runs `checkpw` against a dummy hash to take the same time.
3. If valid: calls `sign_token(...)` — creates a JWT with `sub`, `role`, `displayName`, expires in 7 days
4. Sets the `token` cookie: `HttpOnly`, `Secure`, `SameSite=Strict`, 7-day `max_age`
5. Returns `{ sub, role, displayName }`

Frontend: response goes into `AuthContext.setUser()` → React re-renders → `AppShell` sees `user !== null` → switches to authenticated view.

### Step 4: JWT on every protected request

Every `apiFetch()` call (`web/src/lib/api.ts`) sends the browser's cookies automatically (no explicit headers needed — cookies are same-origin). The `token` cookie is `HttpOnly`, so JavaScript can't read it — only the browser sends it.

Backend: `require_auth` (`api/lib/auth.py`) is a FastAPI dependency. Routes that need auth declare it:

```python
def some_route(user: Annotated[AuthUser, Depends(require_auth)]):
```

`require_admin` (`api/lib/auth.py`) chains on top of `require_auth` — checks `user.role == "admin"`, 403 if not.

### 401 handling: auto-logout

`apiFetch()`: if any request returns 401:
1. Calls `navigation.clearAuth()` — a module-level singleton (`web/src/lib/navigation.ts`)
2. `AppShell` registers `setUser(null)` as the clear function on mount
3. Result: user gets logged out and sees the login page

This handles session expiry without any polling.

---

## Data Layer Architecture

### Frontend: three-layer pattern

Every piece of data follows the same pattern:

```
Page component
    ↓ calls
Hook (e.g. useResults.ts)
    ↓ calls
api.ts function (e.g. getResults)
    ↓ HTTP GET
Backend route
    ↓ calls
lib/db/*.py function
    ↓
DynamoDB table
```

**Hooks use TanStack Query.** Key concepts:
- `useQuery({ queryKey: ['results'], queryFn: getResults })` — fetches once, caches for 2 minutes, auto-deduplicates concurrent calls
- `useMutation({ mutationFn: addResult, onSuccess: () => qc.invalidateQueries(...) })` — writes data, then invalidates the cache so the list re-fetches

### Backend: DB layer (`api/lib/db/`)

Each table has its own file. All files follow the same pattern:

```python
# lib/db/results.py
import lib.db.base as _db

def list_results() -> list[dict]:
    return _db.tables["results"].scan()["Items"]

def get_result(pk: str) -> dict | None:
    resp = _db.tables["results"].get_item(Key={"pk": pk})
    return resp.get("Item")
```

`lib/db/base.py` creates the boto3 DynamoDB table resources at import time using env vars for table names. **One important thing**: floats are rejected by DynamoDB, so `put_result` calls `_floats_to_decimal()` before writing.

**Tables:**
| Table name | DynamoDB name | Env var |
|---|---|---|
| users | boardsite-users | USERS_TABLE |
| games | boardsite-games | GAMES_TABLE |
| results | boardsite-results | RESULTS_TABLE |
| posts | boardsite-posts | POSTS_TABLE |
| recs | boardsite-recs | RECS_TABLE |
| reactions | boardsite-reactions | REACTIONS_TABLE |
| notifications | boardsite-notifications | NOTIFICATIONS_TABLE |
| settings | boardsite-settings | SETTINGS_TABLE |

---

## Page-by-Page Walkthrough

Routes are defined in `web/src/App.tsx`. `AppShell` renders one of two `<Routes>` blocks depending on whether `user` is null: an **unauthenticated** set (landing/login/public pages) or the **authenticated** set (everything behind the nav bar). Page components are all lazy-loaded (`lazy(() => import(...))`) and live in `web/src/pages/`.

### Unauthenticated routes

#### `/` — `LandingPage`

Marketing/splash page shown to signed-out visitors. Fetches public data only: `useRecommended()` (for a 4-item "featured" teaser grid) and `usePublicSettings()` (for the instance display name). No auth required — these are public-safe endpoints. Links to `/login` and `/recommended`.

#### `/login` — `LoginPage`

Calls `login(username, password)` from `lib/api.ts`, then `setUser()` on success and navigates to `?redirect=` or `/`. Handles a 429 (rate-limited) response specially by showing a "try again in N seconds" message; on other failures it calls `checkHealth()` to distinguish "wrong credentials" from "service unavailable." Also displays a toast if it was redirected here after a session expired (`sessionStorage["_expiredRedirect"]`, written by the catch-all route below). Links to `/forgot-password`.

#### `/forgot-password` — `ForgotPasswordPage`

Submits a username to `forgotPassword()`. Always shows the same "if that account exists..." confirmation regardless of whether the username was found — the backend intentionally doesn't reveal account existence.

#### `/reset-password` — `ResetPasswordPage`

Reads a `token` query param; if present, lets the user submit a new password via `resetPassword(token, newPassword)`, then redirects to `/login`. If the token is missing, shows an "invalid or expired" message instead of a form.

#### `/recommended` and `/recommended/:id` — `RecommendedPage` / `RecDetailPage`

Public recommendation pages — also reachable when logged in (see below; they're mounted in both route sets). `RecommendedPage` lists all recommendations (`useRecommended()`) as a card grid; cards link to `/recommended/:slug-or-pk` only if `hasPost` is true. `RecDetailPage` calls `useRecommendedDetail(id)` and renders the full writeup via `SafeHtml`, plus a sidebar of game stats (players, play time, complexity). Both show a sign-in header/footer CTA when `user` is null.

#### `/privacy` — `PrivacyPolicyPage`

Static GDPR-style privacy policy. No data fetching.

#### `*` (catch-all) — `ExpiredRedirect`

Not a page component — a redirect helper. If `sessionStorage["_expiredRedirect"]` is set (written by the 401 handler in `apiFetch`, see Auth Flow above), redirects to `/login?redirect=<path>`; otherwise redirects to `/`. This is why protected paths like `/players/*` must NOT appear in the unauthenticated route list — they need to fall through to this catch-all so a session-expiry redirect-back can fire.

### Authenticated routes

#### `/` — `HomePage`

Dashboard shown once logged in. Calls `useResults()` and `useStats()` to show: sessions logged this week, the user's wins this week, the most-played game, a "recent sessions" list, and a top-5 standings preview (links to `/leaderboard`). Admins get a "Log Play" button that opens `LogResultDialog`; readonly users see the same button disabled with a tooltip.

#### `/catalog` — `Catalog`

Renders `<GamePicker>` (the searchable/filterable game grid component). Admins get an "Add Game" button (`AddGameDialog`) and a delete action on each card (`useDeleteGame()`); readonly users see neither.

#### `/picker` — `Picker`

A "what should we play tonight" randomizer. Client-side filters (player count, max time, complexity) narrow `useGames()`'s list, then "Surprise me!" picks a random match from the filtered set with a short fake-rolling animation before revealing a `GameCard`.

#### `/log` — `LogResult`

The session history / chronicle page (despite the route name, this is the results timeline, not a single-log form). Groups `useResults()` by month and renders a timeline with game thumbnails, winner, mood emoji, and player avatars. Admins can edit/delete each entry inline (`LogResultDialog` in edit mode) and see a "Write post" link for sessions without a linked post; everyone sees `SessionReactions` per session.

#### `/leaderboard` — `Leaderboard`

Calls `useStats()` for the full Elo-style leaderboard: a 3-slot podium for the top players, the full `LeaderboardTable`, most-played game, win streaks, `HeadToHead` matchup grid, a `WinRaceChart`, a `MonthlyChart` of sessions per month, and a per-game stats breakdown (`GameStatCard`, expandable for player/seat/variable stats). Links to `/records` for all-time records.

#### `/games/:id` — `GameDetailPage`

Looks up the game by `idFromPk` match against `useGames()`, then derives session count, player win/loss stats, average/high score, and session history from `useResults()` and `usePosts()` filtered to that game. Admins see "Configure" (`GameConfigDialog`, for per-player variables/seats) and "Log this game" (`LogResultDialog` pre-filled with this game) buttons.

#### `/players/:id` — `PlayerProfilePage`

The most data-dense page. Combines `usePlayerStats(id)` (achievements, win-rate trend, per-game stats), `useResults()`, `useGames()`, and `useStats()` (for the player's Elo rank) into: a hero card with avatar/stats, current/best win streaks, favorite game, nemesis/"favourite prey" (head-to-head records requiring 2+ shared games), an achievements grid (`AchievementBadge`), win-rate and score trend charts, a "Game Passport" (visual grid of played vs. unplayed games), and recent sessions. `canEdit` (own profile or admin) unlocks avatar upload/removal (`uploadAvatar`/`deleteAvatar`, with an optimistic local-preview URL before the real CDN URL lands) and a "My Wrapped" button that opens `WrappedOverlay` — a Spotify-Wrapped-style slideshow built from the same stats.

#### `/posts` — `PostsPage`

Lists all posts (`usePosts()`) as `PostCard`s, sorted newest first. Admins get a "New Post" button linking to `/posts/new`.

#### `/posts/new` and `/posts/:id/edit` — `PostEditorPage`

Same component for both create and edit (`isEdit = Boolean(id)`). Requires picking an existing session from a dropdown (`useResults()`) — a post is always tied to a session, and submitting copies that session's `gameName`/`gameId` onto the post. Content is edited via `TiptapEditor`. Autosaves a local draft (`useDraft`, keyed by `post-draft:<id-or-new>`) every second and offers to restore it if it differs from the loaded content — guards against losing work on an accidental navigation. New posts can pre-fill the session via `?session=<pk>` (linked from the `/log` page's "Write post" action).

#### `/posts/:id` — `PostViewPage`

Renders the post's `content` through `SafeHtml`, plus the linked session's date/players/winner if found. Admins see Edit (→ `/posts/:id/edit`) and Delete (with a `window.confirm` guard) actions.

#### `/users` — `UsersPage` (admin only)

Not present in the route list at all for non-admins — `AppShell` only adds this `<Route>` when `user.role === "admin"`. Lists all users (`getUsers`) with create/edit/delete dialogs (`createUser`/`updateUser`/`deleteUser`). Blocks a user from changing their own role and hides the delete button on your own row.

#### `/admin/recommended` — `AdminRecommendedPage` (admin only)

CRUD for the recommendations shown on `/recommended`. Each entry picks an existing game (search-as-you-type against `useGames()`), a blurb, comma-separated tags, a "best for" string, and a manual `order` (with up/down buttons that swap `order` values between adjacent rows via two sequential `updateRec` calls). "Write Post"/"Edit Post" links to `/admin/recommended/:id/edit` for the long-form writeup.

#### `/admin/recommended/:id/edit` — `RecEditorPage` (admin only)

A focused full-screen `TiptapEditor` for the recommendation's long-form `content` field (separate from the short `blurb` edited in the dialog above). Saves via `useUpdateRecommended()` and navigates back to `/admin/recommended`.

#### `/admin/settings` — `SettingsPage` (admin only)

Three independent forms (`BrandingCard`, `IntegrationsCard`, `InstanceUrlCard`), each its own `useMutation` calling `updateSettings()` and invalidating `["settings"]` on success: instance display name, the BGG API token (write-only — only shows whether one is set, never its value, with a "Clear token" action), and the public base URL used for password-reset email links (falls back to the server's `APP_BASE_URL` env var if left blank).

#### `/records` — `RecordsPage`

All-time stats derived client-side from `useResults()` and `useStats()`: longest win/loss streaks, busiest day, first game ever logged, total sessions, unique games played, the all-time Elo champion, and the most active month.

#### `/login` (authenticated)

Mounted as `<Route path="/login" element={<Navigate to="/" replace />} />` — if a logged-in user somehow lands on `/login`, they're bounced straight to `/`.

---

## Key Patterns to Know

### `apiFetch` vs bare `fetch`

- **`apiFetch`** (`web/src/lib/api.ts`): adds base URL, sends cookies, handles 401 auto-logout, throws on non-2xx. Use for authenticated endpoints.
- **bare `fetch`**: used for public endpoints (`/api/recommended`, `/api/recommended/:id`) that don't need the auth cookie or 401 handling.

### `idFromPk`

```typescript
// web/src/lib/utils.ts
export function idFromPk(pk: string): string {
  return pk.includes('#') ? pk.split('#')[1] : pk
}
```

DynamoDB items have pks like `GAME#01ABC` or `PLAYER#01ABC`. URLs use just the `01ABC` part. This function extracts it. Rec pks are bare ULIDs (no prefix) so `idFromPk` returns them unchanged.

### Query invalidation

When you mutate data, you invalidate the relevant cache keys:

```typescript
qc.invalidateQueries({ queryKey: ['results'] })  // re-fetches results list
qc.invalidateQueries({ queryKey: ['stats'] })     // re-fetches leaderboard
```

Invalidating `['recommended']` also invalidates `['recommended', id]` (prefix match) — so the detail page re-fetches after an edit.

### `SafeHtml`

All user-authored HTML (post content, rec content) renders through `<SafeHtml>`. It sanitizes the HTML with DOMPurify before inserting it into the DOM. Never skip this for user-provided HTML.

### Toast notifications

`toast.success(...)` and `toast.error(...)` from `sonner`. The `<Toaster>` is mounted in `main.tsx` — it works from anywhere without prop drilling.

---

## Request Flow Summary (one request, end-to-end)

Example: user views `/log`, results load.

```
Browser: GET /api/results
    ↓ (via Vite proxy in dev, CloudFront in prod)
main.py: origin_guard middleware
    ↓ _initialize() (no-op after first call)
    ↓ DEV_MODE=true → skip token check
    ↓ call_next(request)
results.py: GET "" handler
    ↓ require_auth(token cookie) → decode JWT → AuthUser
    ↓ list_results()
lib/db/results.py: list_results()
    ↓ _db.tables["results"].scan()
DynamoDB: full table scan → returns all items
    ↓
results.py: returns list as JSON
    ↓
Browser: TanStack Query caches as queryKey=['results']
    ↓
LogResult.tsx: useResults() returns { data: results }
    ↓
React renders result cards
```

---

## Where Breakpoints Pay Off

| Symptom | Where to look |
|---|---|
| Blank page / spinner forever | `AuthContext.tsx`'s `useEffect` — is `getCurrentUser` hanging? |
| Logged out unexpectedly | `api.ts`'s 401 handler — 401 from which endpoint? |
| Wrong user sees wrong content | `require_auth` in `lib/auth.py` — which token? |
| Data not refreshing after mutation | hook's `onSuccess` — is `invalidateQueries` firing? |
| 403 on API call in production | `main.py` — is `x-origin-token` missing? |
| DynamoDB write failing | `lib/db/base.py`'s `_floats_to_decimal` — float in payload? |
| Post/result not appearing in list | DB `scan()` call — did `createdAt` get set? (GSI requires it) |
| BGG search broken | `api/routes/games.py` — BGG token loaded from SSM? |
| Slug URL not working | `api/routes/recommended.py`'s `get_recommended` — pk vs slug fallback |
