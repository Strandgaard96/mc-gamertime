# Contributing

Thanks for taking a look. This page is enough to get the app running, make a change, and
check it before opening a PR — no need to read the docs site first.

## Repository layout

| Path | What it is |
|---|---|
| `api/` | Python / FastAPI backend. Runs under uvicorn when self-hosted, on AWS Lambda via Mangum in the cloud deployment |
| `web/` | React + Vite single-page app (TypeScript, Tailwind, TanStack Query) |
| `infra/` | Terraform for the optional AWS deployment |
| `docs-site/` | The documentation site (Astro Starlight) |
| `scripts/`, `api/scripts/` | Admin and maintenance CLIs (create users, export tables, backups) |

## Prerequisites

- [uv](https://docs.astral.sh/uv/) for Python — `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Node.js 20 or newer
- Docker, only if you want to run the packaged container

You do **not** need an AWS account. The app defaults to self-hosted: embedded SQLite and
local file storage.

## Run it

The quickest way to see the whole thing running is the container:

```bash
docker compose up -d          # http://localhost:4263
```

For development you usually want the two dev servers instead, with hot reload on both
sides. Backend first:

```bash
cd api
SQLITE_DB_PATH=./dev.db \
LOCAL_STORAGE_DIR=./dev-storage \
JWT_SECRET=dev-secret-not-for-production \
ADMIN_USERNAME=admin ADMIN_PASSWORD=devpassword123 \
DEV_MODE=true \
uv run uvicorn main:app --reload --port 8000
```

The three paths/secrets are the only required settings — everything else already defaults
to the self-hosted backends. `ADMIN_USERNAME`/`ADMIN_PASSWORD` create an admin account on
first boot and are ignored afterwards. `DEV_MODE=true` skips the CloudFront origin check,
which has nothing to enforce locally.

Then the frontend, in a second terminal:

```bash
cd web
npm install
npm run dev                   # http://localhost:5173
```

Vite proxies `/api/*` to port 8000, so the backend must be on that exact port.

VS Code users: press **F5** and pick **Full Stack** to start both with debuggers attached.

## Before you open a PR

These are the same checks CI runs, so running them locally avoids a red build:

```bash
cd api && uv run pytest tests/ -v     # backend tests
cd api && uv run ruff check . && uv run ruff format --check .
cd web && npm run test                # frontend tests
cd web && npm run typecheck           # tsc --noEmit
cd web && npx oxlint src/
```

Optionally install the git hooks, which run the linters and type checkers plus a secret
scan and a dependency-CVE scan on every commit. They are managed by
[prek](https://prek.j178.dev/), a drop-in replacement for pre-commit (same
`.pre-commit-config.yaml`, single binary, faster); `pre-commit` itself works too:

```bash
uv tool install prek
prek install
```

The CVE hook needs [trivy](https://trivy.dev/latest/getting-started/installation/) on your
PATH; it only runs when a lockfile or the `Dockerfile` changes.

## Commit messages

This repo uses [Conventional Commits](https://www.conventionalcommits.org/) — `feat:`,
`fix:`, `docs:`, `chore:`, `refactor:`, `test:`, `ci:`. It isn't a style preference:
`release-please` reads these to decide the next version number and to write
`CHANGELOG.md`, so an unprefixed commit is invisible in the release notes.

If you change the SQLite schema, add a migration to `api/lib/db/migrations.py` and put a
`BREAKING CHANGE:` footer in the commit so self-hosters see it before upgrading.

## Pull requests

- One thing per PR, and keep it small enough to review in one sitting
- Tests must pass, and new behaviour should come with a test
- Fill in the PR template

## Questions

Open an issue — the bug and feature templates cover the usual cases, and setup questions
are welcome there too.

More detail — architecture walkthrough, common recipes, debugging tips — lives in the
[contributor docs](https://mcgamertime-docs.drmaggi.com/contributing/overview/).
