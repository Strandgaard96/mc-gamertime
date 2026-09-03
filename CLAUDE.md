# Board Game Night
GitHub repo: https://github.com/Strandgaard96/mc-gamertime

Monorepo: `api/` (Lambda/Python/FastAPI), `web/` (React/Vite), `infra/` (Terraform), `scripts/`.
Branch: `main` (pushed to `origin/main`)

## Commands

`cd web && npx tsc --noEmit` — typecheck web (must run from web/ dir)
`cd api && uv run pytest tests/ -v` — run API tests
`task build` — `api/build.sh` (lambda.zip) + `vite build` web/
`task plan` — terraform plan (check infra diff before deploy)
`task deploy` — build + terraform apply + S3 sync + CF invalidation
`task users` / `task users:dev` — list all users (prod / dev table)
`task create-user -- --username alice --display-name 'Alice' --role readonly --password secret [--env dev]` — create user
`task update-user -- --username alice --password newsecret [--display-name '...'] [--role admin] [--env dev]` — update password/display name/role
`task delete-user -- --username alice [--env dev]` — delete user
`task revoke-sessions -- --username alice [--env dev]` — invalidate all sessions for a user
`cd web && npm run dev` — frontend only (localhost:5173), needs API running separately
`cd api && uv run uvicorn main:app --reload --port 8000` — API only (localhost:8000), set `DEV_MODE=true`
`cd api && API_URL=https://<your-domain>/api uv run python3 scripts/seed-games.py --username admin --password <pw>` — seed game catalog
http is the command from the httpie package used instead of curl on this site. Use context7 for documentation.

## Local Development (VS Code)

The project includes a **"Full Stack" VS Code Launch Configuration**:

1.  **Launch:** Press **F5** in VS Code and select **"Full Stack"**.
2.  **What happens:** Starts FastAPI (`localhost:8000`) and Vite (`localhost:5173`) automatically.
3.  **Environment:** API runs with `DEV_MODE=true` to bypass production CloudFront origin-token security.
4.  **Database:** Uses real AWS credentials (ensure `aws configure` is run).

### First-time Setup
1.  Bootstrap admin: `cd api && uv run python3 scripts/create-user.py --username admin --display-name "Admin" --role admin --password <pw>`

### Python dev with uv
`uv run <cmd>` — run command in project venv (auto-syncs deps, no activation needed)
`uvx <tool>` — run a tool ephemerally without installing it (e.g. `uvx ruff check .`)
`uv sync` — create/update `.venv/` from `pyproject.toml` (run from `api/`; done automatically by F5 preLaunchTask)
`uv add <pkg>` — add dep to `pyproject.toml` and sync; `uv remove <pkg>` to remove

## Key Patterns

- DynamoDB `type` is reserved word → use `ExpressionAttributeNames: {'#t': 'type'}` in all queries
- DynamoDB rejects Python floats → `db_put` auto-converts via `_floats_to_decimal()` in `lib/dynamo.py`
- DynamoDB GSI `type-index` requires BOTH `type` AND `createdAt` on items — missing `createdAt` silently excludes item from index; all new items must include `createdAt`
- DynamoDB `update_item` calls are never written directly in `lib/db/*.py` — use
  `add_to_set`/`remove_from_set`/`increment_with_timestamp` on the table object
  (`lib/db/base.py::DynamoTable`, mirrored by `lib/db/sqlite_backend.py::SqliteTable`) so both
  backends stay in sync.
- BGG search: `GET /api/games/search?q=`, detail: `GET /api/games/search?bggId=`
- BGG API requires `Authorization: Bearer <token>` — token in SSM `/boardsite/bgg-token`, fetched at cold start
- `apiFetch` handles 204: `if (res.status === 204) return undefined as T` before `.json()`
- `formatDate` uses `en-US` locale → "May 21, 2026" format
- `pluralize(count, singular, plural?)` in `web/src/lib/utils.ts` returns `"${count} ${word}"` (count already included) — call as `{pluralize(n, "session")}`, never `` `${n} ${pluralize(n, "session")}` `` (double-counts)
- Python deps managed via uv + `pyproject.toml` in `api/` — run pytest as `cd api && uv run pytest`; never activate venv manually
- **`build.sh` packages Lambda deps from `api/requirements.txt`, NOT `pyproject.toml`/`uv.lock`** — adding a package needs BOTH `uv add <pkg>` (tests) AND a pinned line in `requirements.txt` (deploy). Miss the second → `Runtime.ImportModuleError: No module named '<pkg>'` crashes EVERY route at cold start (tests stay green, since they run in the uv venv where the dep exists). Verify before deploying: `cd api && ./build.sh && ls dist/ | grep <pkg>`
- Starlette 1.0.1 deprecated per-request cookies — use `client.cookies.set()` on TestClient instead
- FastAPI `redirect_slashes=False` — all routes use `""` not `"/"` to avoid 307 leaking API Gateway URL
- `task build && task apply` deploys Lambda via `source_code_hash` — no manual AWS CLI needed
- Blog images: S3 `blog-images/` prefix, presigned PUT via `POST /api/posts/upload`. The
  returned read URL is **relative** (`/blog-images/<ulid>.png`) on every deployment — media is
  served by the app behind `require_auth`, never straight from S3/CloudFront. An absolute CDN
  URL would be cross-site and the `SameSite=Strict` cookie wouldn't be sent.
- posts.py: `POST /upload` declared before `GET /{post_id}` — order prevents route shadowing
- SafeHtml component: DOMPurify + DOMParser + replaceChildren — use for all HTML rendering in blog
- DynamoDB table names: `boardsite-users`, `boardsite-games`, `boardsite-results`, `boardsite-posts`, `boardsite-recs`, `boardsite-notifications`, `boardsite-settings` — override via env vars `USERS_TABLE`, `GAMES_TABLE`, `RESULTS_TABLE`, `POSTS_TABLE`, `RECS_TABLE`, `NOTIFICATIONS_TABLE`, `SETTINGS_TABLE`
- pk format: bare ULID for games/results/posts, username string for users/players — `idFromPk(pk)` in `web/src/lib/utils.ts` strips any `PREFIX#value` prefix (use for URL routing)
- `cn(...classes)` in `web/src/lib/utils.ts` — clsx + tailwind-merge; use for conditional className merging
- `Button` (`web/src/components/ui/button.tsx`) supports `asChild` (via `cloneElement`, no Radix dep) — use `<Button asChild><Link to="...">label</Link></Button>` instead of `<Link><Button>...</Button></Link>` (invalid nested `<a><button>`). Known remaining instances not yet converted: `PostViewPage.tsx:76`, `AdminRecommendedPage.tsx:139,146`.
- DynamoDB list queries: use `paginated_scan(_db.tables["x"])` from `api/lib/db/base.py` — never `table.scan()["Items"]` directly (truncates at 1MB)
- `api/lib/rate_limit.py`'s `Limiter(..., headers_enabled=True)` requires every
  `@limiter.limit(...)`-decorated route to declare a `response: Response` parameter (even if
  unused in the body) — slowapi throws trying to inject rate-limit headers otherwise.
- API test fixtures: `authed_client()` returns a factory — call as `authed_client("admin")` or `authed_client("readonly")`; pass `headers=ORIGIN` (`{"x-origin-token": "test-origin-token"}`) on every request
- PUT/edit routes (`posts.py`, `recommended.py`, `results.py`) use `body.model_dump(exclude_unset=True)` merge semantics: omitted field → unchanged, explicit `null` → clears the field. Validators for nullable fields must accept `| None` and short-circuit on `None`.
- `api/lib/achievements/` package (`defs.py` rule defs, `engine.py` exposes `compute_achievements(player_id, results, games_by_id) -> [{id, label, description, icon, earnedAt}]`, re-exported via `__init__.py`). New achievement = 1 def entry + rule + tests in `test_achievements.py`.
- Detecting "newly happened" events (milestones, achievements) on `create_result`: build `before_results = [r for r in list_results() if r.get("pk") != result["pk"]]`, then `all_results = before_results + [result]`. Required because real DynamoDB scans are eventually consistent (new write may or may not appear) while `FakeTable.scan()` in tests is synchronous (always appears) — excluding-then-appending by known pk is correct under both. See `detect_milestone`/`_detect_new_achievements` in `api/routes/results.py`.
- **Conventional Commits:** Use `feat:`, `fix:`, `chore:`, etc. in commit messages. This is **required** for GitHub Actions (specifically `release-please`) to automatically generate changelogs and manage versioning.
- Per-player notification inbox: `api/lib/db/notifications.py` (`put_notification`, `list_notifications_for_player`); `GET /api/notifications` → `{notifications, unreadCount}` (unread = `createdAt > user.lastReadAt`); `POST /api/notifications/read` → `set_last_read_at` in `api/lib/db/users.py`.
- Optional result fields handle `None` differently: top-level (`mood`) is popped from the dict before `put_result` (attribute absent); nested `ResultPlayer.score: None` is stored as DynamoDB NULL via `_floats_to_decimal`. Match the existing field's pattern, don't assume they're interchangeable.
- `playerVariables[].id` is server-derived (slugified label via `_assign_variable_ids` in `api/routes/games.py`) and **changes if the label is edited** — `_validate_player_config` in `api/routes/results.py` requires the `variables` dict's keys to be EXACTLY the current `playerVariables[].id` set (422 on any mismatch, including stale ids). Frontend forms (`LogResultDialog`) must reset `variables`/`seats` state on game switch and build the payload from the *current* `playerVariables` list, not from stale per-player state — otherwise edits after a label rename 422.
- Storage proxy (`api/routes/storage.py`) has its own hardcoded `_ALLOWED_PREFIXES` tuple,
  independent of any upload endpoint's S3 key prefix — adding a new image-upload feature (new
  prefix) needs this allowlist updated too, or every upload/read 403s. It now gates **both**
  deployments: `media_router` is mounted at `/avatars`, `/blog-images` and `/game-images` on
  every deployment, and `infra/cloudfront.tf` routes those three prefixes to Lambda instead of
  S3. A new prefix therefore needs the tuple, a `media_router` mount, a CloudFront behaviour,
  the Lambda IAM resource list, and the `Deny` in `infra/s3.tf` — miss the last two and it is
  either unreadable or world-readable.
- PUT/edit routes' `exclude_unset` merge (above) has a frontend-side trap: `JSON.stringify` drops `undefined` values, so a form that sends `undefined` for a blanked field gets treated as "field unchanged," not "field cleared." To actually clear an optional field, send explicit `null`.

## Infra Notes

- **`infra/terraform.tfvars` is required and gitignored** — holds every deployment-specific
  value that must not be in source: `domain` (no default; apply fails without it),
  `cloudfront_web_acl_arn` (embeds the AWS account id; **empty value disassociates the prod
  WAF ACL** — never apply prod without it set), `extra_cors_origins`. Copy
  `infra/terraform.tfvars.example` to start. Losing this file = broken prod apply, so keep it
  backed up outside the repo.
- ACM cert created in us-east-1 (provider alias) — CloudFront requirement
- No Route53 — DNS managed manually in Cloudflare (CNAME `games → <distro>.cloudfront.net`, proxied=off)
- After first `task apply`: output ACM validation CNAMEs → add in Cloudflare → wait ~2 min → `task apply` again
- API: CloudFront → API Gateway HTTP API → Lambda (Lambda Function URL had persistent 403 on this account tier)
- Lambda Function URL NOT used — API Gateway is the invoke path
- CloudFront custom error pages intercept 403+404 from ALL origins — Lambda errors served as `index.html` (200); detect with `x-cache: Error from cloudfront` header
- `bgg_token` Terraform var only needed on first apply — SSM param uses `lifecycle.ignore_changes`, subsequent applies don't require it
- Stale TF lock after crash: `ps aux | grep terraform` → kill PID, then retry; `terraform force-unlock` doesn't work on local state
- CloudFront free pricing plan doesn't support custom response headers policies — don't add `aws_cloudfront_response_headers_policy` without upgrading plan first

## Dev Environment

- Separate Terraform workspace `dev` (prod = `default`) — `terraform.workspace`-derived `env_suffix`/`fqdn`/`name_prefix` make every resource name/domain workspace-specific, zero-diff for prod
- Commands: `task plan:dev`, `task apply:dev` (terraform only), `task deploy:dev` (test + build + apply + S3 sync + CF invalidation) — all auto-select `dev` workspace and switch back to `default` after
- URL: `https://games-dev.<domain>` (from `local.fqdn` in the `dev` workspace) — Cloudflare CNAME → dev CloudFront `cloudfront_url` output (proxied=off)
- DynamoDB tables: `boardsite-{users,games,results,posts,recs}-dev` — independent data, isolated from prod
- SSM secrets (`jwt-secret`, `origin-token`, `bgg-token`) are **shared with prod** — owned by `default` workspace, dev reads via `data "aws_ssm_parameter"` (see `infra/ssm.tf`)
- **Dev has no WAF.** `infra/waf.tf` and `var.dev_allowed_ips` were removed; `cloudfront.tf` attaches `var.cloudfront_web_acl_arn` only in the `default` (prod) workspace, so the dev distribution is reachable from the internet and protected by login alone. Don't put anything in dev you wouldn't put in prod.
- Dev admin credentials: generated and stored in repo-root `.env` (gitignored, never commit) as `DEV_ADMIN_USERNAME`/`DEV_ADMIN_PASSWORD`
- `.vscode/launch.json` stays generic (`ENV`/`DEV_MODE` only) and loads everything else from
  repo-root `.env` via `envFile` — that file must define `AWS_REGION`, `S3_BUCKET`,
  and the eight `*_TABLE` names for the dev stack, or F5 hits prod defaults (`CLOUDFRONT_URL` is
  no longer read by the app — media URLs are relative now)
- `task deploy:dev` rebuilds the shared `api/lambda.zip` — afterwards `task plan` (prod) may show a Lambda `source_code_hash` diff until prod is separately redeployed with the same build
- If your own DNS resolves the app's domain to something local (split-horizon DNS, a LAN reverse proxy), point scripts at the `*.cloudfront.net` distribution domain instead: an intercepting 301 turns POSTs into GETs and requests fail in confusing ways.

## Self-Hosted Mode

Docker Compose stack (single `app` container) for running this app outside AWS — fully
additive, does not affect `infra/`/`task build`/`task deploy`.

- No setup script — copy `.env.example` to `.env` next to `docker-compose.yml` (compose
  auto-loads it) to set BGG token, PUID/PGID, etc. `.env` is fully optional; the stack runs
  fine without one.
- `docker compose up -d --build` — builds the image (root `Dockerfile`, multi-stage: `web/` → Vite build → `api/` runtime) and starts the stack
- `docker compose exec app python3 scripts/create-user.py --username admin --display-name "Admin" --role admin --password <pw>` — bootstrap first admin
- One exposed port, same number both sides (`${APP_PORT:-4263}:4263` on `app`). The container
  binds 4263 in `docker/entrypoint.sh` and `Dockerfile`'s HEALTHCHECK — change one and the
  healthcheck fails the container forever. `APP_PORT` is the one self-host env var that must
  NOT go in the compose `environment:` block: it is read by docker-compose, not the app.
  Local dev is unrelated and stays on 8000 (vite proxy target).
- **Selfhost is the DEFAULT everywhere; AWS is opt-in.** Unset env = SQLite + local files + env
  secrets + no origin guard + no public recommended. The Dockerfile bakes the same five values in
  (so bare `docker run` works with zero config), and `infra/lambda.tf` names the cloud values
  explicitly (`DB_BACKEND=dynamodb`, `STORAGE_BACKEND=s3`, `SECRETS_PROVIDER=ssm`,
  `ORIGIN_GUARD_ENABLED=true`, `PUBLIC_RECOMMENDED_ENABLED=true`). Consequences: any *new* AWS
  entry point (script, Lambda, task) must set `DB_BACKEND=dynamodb` or it silently reads a local
  SQLite file — this is why the `task users`/`create-user`/... targets carry that prefix.
  `api/tests/conftest.py` pins it too, since `lib/db/base.py` builds tables at import time and
  the SQLite default would touch `/data/`.
- Env-var branches: `DB_BACKEND=sqlite` (embedded SQLite file
  instead of DynamoDB, see `api/lib/db/sqlite_backend.py`), `STORAGE_BACKEND=local` (local
  filesystem instead of S3, see `LocalFsClient` in `api/lib/storage.py`),
  `SECRETS_PROVIDER=env` (reads `JWT_SECRET`/`ORIGIN_TOKEN`/`BGG_TOKEN` from env, not SSM),
  `STATIC_DIR` (serves `web/dist` via FastAPI + SPA fallback), `ORIGIN_GUARD_ENABLED=false`,
  `PUBLIC_RECOMMENDED_ENABLED=false`, `CORS_ALLOWED_ORIGINS` (comma-separated credentialed CORS
  peers; empty = same-origin only, which is the normal selfhost setup. Cloud path gets it from
  `infra/lambda.tf`, derived from `local.fqdn` + `var.extra_cors_origins` — no domain is
  hardcoded in `api/main.py`)
- `FORWARDED_ALLOW_IPS` (uvicorn `--forwarded-allow-ips`, default
  `127.0.0.1,::1,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16` set in `docker/entrypoint.sh`
  — trusts X-Forwarded-For from private/Docker-internal ranges so the rate limiter
  sees real client IPs behind any documented reverse proxy; see
  `api/tests/test_proxy_headers.py`)
- `JWT_SECRET` auto-generated on first boot, persisted to `/data/.jwt_secret` in the bind-mounted
  `config/app/` directory (never in `.env`, never served)
- Self-service password reset: `POST /api/auth/forgot-password` / `POST /api/auth/reset-password`
  (`api/routes/auth.py`) — JWT reset token (`sign_reset_token`/`decode_reset_token` in
  `lib/auth.py`) keyed to `tokenVersion` for single-use; stdlib SMTP mailer
  (`lib/mailer.py`, gated on `SMTP_HOST` — empty logs the link to stdout instead of sending).
  Reset-link host comes from `APP_BASE_URL` if set, else falls back to the request's `Host`
  header (spoofable if you expose the app's port directly without a reverse proxy — set
  `APP_BASE_URL` in production).
- `METRICS_ENABLED=true` exposes a Prometheus-format `/metrics` (`api/lib/metrics.py`) — off by
  default, no import/registration cost on the Lambda path when unset. No auth beyond whatever
  `ORIGIN_GUARD_ENABLED` already enforces.
- `scripts/create-user.py` run with zero args on a real TTY prompts interactively instead of
  erroring on missing flags; any args, or no TTY (piped/`exec -T`), keeps the old argparse
  behavior unchanged.
- New self-host env var/feature → update ALL 4 surfaces or docs silently diverge: `.env.example`,
  `docker-compose.yml` (`app.environment:` passthrough — vars not listed there never reach the
  container), `docs-site/.../self-hosting/configuration.mdx`, and this section. (`docs/selfhost.md`
  was a 5th surface until it was deleted as a pre-docs-site duplicate — don't recreate it.)
- `create-user.py`'s interactive wizard uses `getpass.getpass()`, which opens `/dev/tty` directly
  and ignores redirected stdin — can't be driven by a heredoc/pipe in a non-interactive shell or
  by a subagent; only testable by a human at a real terminal.
- Security audits of the live deployment live in top-level `audits/`, which is **gitignored** —
  they map the prod attack surface and must never be published. Plans/specs describing shipped
  fixes stay tracked in `superpowers/`.
- Planning artifacts (specs/plans from past sessions) live in top-level `superpowers/{plans,specs}/`,
  not under `docs/` — `docs/` was deleted (it only ever held stale pre-docs-site duplicates); the
  `writing-plans`/`subagent-driven-development` skills default to `docs/superpowers/plans/...`,
  override that and save new plans/specs under `superpowers/` instead.
- All user-facing docs live in `docs-site/` (Starlight, published to mcgamertime-docs.drmaggi.com) —
  there is no root-level `docs/` anymore. Don't recreate root `.md` doc files; add a docs-site page.

- `/storage/*` proxy (`api/routes/storage.py`, registered only when `STORAGE_BACKEND=local` or
  `S3_ENDPOINT_URL` set): `require_auth`-gated; GET/HEAD restricted to `avatars/`/`blog-images/`/
  `game-images/` prefixes (the bucket also holds `exports/` table dumps from
  `scripts/export-tables.py` — must stay unreachable via this proxy); PUT forwards
  presigned-upload bytes to the storage backend preserving the signed `Host`
- Manual QA without touching real AWS/DynamoDB: run the API with `DB_BACKEND=sqlite
  STORAGE_BACKEND=local SECRETS_PROVIDER=env ORIGIN_GUARD_ENABLED=false SQLITE_DB_PATH=...
  LOCAL_STORAGE_DIR=... JWT_SECRET=... ORIGIN_TOKEN=... DEV_MODE=true uv run uvicorn main:app
  --port 8000` (must be port 8000 — `web/vite.config.ts`'s dev proxy target is hardcoded there),
  then bootstrap an admin via `scripts/create-user.py` with the same env vars.

- See `docs-site/src/content/docs/self-hosting/` for env var reference, backups, upgrades, troubleshooting (live at mcgamertime-docs.drmaggi.com/self-hosting/) — the old `docs/selfhost.md` was a pre-docs-site duplicate, deleted once docs-site covered everything in it

## Debugging Prod

- "Every route 500s identically" (login, players, me, recommended all failing the same way) = Lambda cold-start crash, not a route bug — check `Runtime.ImportModuleError` first: `aws logs filter-log-events --log-group-name /aws/lambda/<resource_prefix>-api --region <region> --filter-pattern "ERROR"` (function name is `${var.resource_prefix}-api`; `terraform output` if unsure)

## Auth Notes

- JWT secret: SSM `/boardsite/jwt-secret`, origin token: SSM `/boardsite/origin-token`, BGG token: SSM `/boardsite/bgg-token` (all SecureString, fetched at cold start)
- CloudFront sends `x-origin-token` header → Lambda validates in `origin_guard` middleware (blocks direct API Gateway calls)
- Roles: `admin` (full CRUD) | `readonly` (no admin CRUD, but MAY still do per-user social writes: reactions, comments, favorites, own avatar — these gate on `require_auth`, not `require_admin`, by design) — set in DynamoDB `users` table
- Auth routes: `POST /api/auth/login` → JWT cookie, `POST /api/auth/logout`; protected routes use `require_auth` + optional `require_admin`
- Bootstrap first admin: `cd api && AWS_REGION=eu-west-1 uv run python3 scripts/create-user.py --username admin --display-name "Name" --role admin --password <pw>`
- `_bootstrap_admin_user()` (`api/main.py`) runs ONLY in the `SECRETS_PROVIDER=env` branch of
  `_initialize()` — i.e. selfhost. The cloud path takes the SSM branch and never creates a user,
  so AWS deploys need `task create-user` or the login page has no valid account. Selfhost with a
  fresh DB and no `ADMIN_USERNAME`/`ADMIN_PASSWORD` is worse: `_initialize()` raises,
  `origin_guard` turns it into 503 on EVERY request including `/`, while Docker still reports the
  container healthy (the HEALTHCHECK only opens a TCP socket). `create-user.py` fixes it live, no restart.
- WAF ACL association must stay in Terraform state — if drift detected, import before apply (never delete/recreate)

## Restore Procedures

**DynamoDB restore (bad deploy or accidental delete):**
PITR window: 35 days. Restore to any second within that window.

```bash
# 1. Restore table to a point-in-time (creates new table)
aws dynamodb restore-table-to-point-in-time \
  --source-table-name boardsite-results \
  --target-table-name boardsite-results-restored \
  --restore-date-time "2026-05-25T10:00:00Z" \
  --region eu-west-1

# 2. Wait for restore to complete (status: ACTIVE)
aws dynamodb describe-table \
  --table-name boardsite-results-restored \
  --region eu-west-1 \
  --query 'Table.TableStatus'

# 3. Option A: swap Lambda env var to point at restored table temporarily
#    infra/variables.tf → change results_table_name default → task apply
# 4. Option B: export items from restored → import into original
#    aws dynamodb scan --table-name boardsite-results-restored > restored.json
#    # then re-import with put-item or a script
```

**S3 image restore (deleted or overwritten blog image):**
*Note: Deployments via `task deploy` preserve images by excluding the `blog-images/` prefix from the S3 sync. These procedures are for manual deletions or overwrites.*

```bash
# List all versions of an object
aws s3api list-object-versions \
  --bucket <your-web-bucket> \
  --prefix blog-images/my-image.jpg

# Restore a specific version by copying it back as current
aws s3api copy-object \
  --copy-source "<your-web-bucket>/blog-images/my-image.jpg?versionId=<VERSION_ID>" \
  --bucket <your-web-bucket> \
  --key blog-images/my-image.jpg \
  --region eu-west-1
```

## Git Notes

- Subagents CAN run `git commit` and `git push` in this environment — no permission block observed in practice (despite earlier assumption otherwise)
- Subagents dispatched via the Agent tool do NOT automatically inherit a worktree the controller switched into — their shell can default to the original repo checkout even with explicit "work from `<path>`" prompt instructions. Seen once: a one-line fix subagent committed straight to `main`. Mitigation: tell every dispatched subagent to verify `git rev-parse --show-toplevel` equals the worktree path immediately before its final commit and abort if not; for small/well-understood fixes, just apply them directly instead of redispatching.
- `EnterWorktree`/`git worktree add` defaults to branching from `origin/<default-branch>` ("fresh"), not local HEAD — local-only commits on `main` that haven't been pushed are missing from a freshly created worktree. Cherry-pick them in if the new worktree needs them.

# CLAUDE.md

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.
