---
title: Contributing
description: How to run tests and submit pull requests.
sidebar:
  order: 1
---

## Running tests

```bash
cd api
uv run pytest tests/ -v
```

Requires [uv](https://docs.astral.sh/uv/) installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`). Tests use an in-memory fake DynamoDB — no AWS credentials or running stack needed.

## First-time setup

Install [pre-commit](https://pre-commit.com/) and activate the hooks:

```bash
pip install pre-commit
cd web && npm install   # required so the oxlint/oxfmt hooks find node_modules
cd ..
brew install trivy      # or see https://trivy.dev/latest/getting-started/installation/ — required for the trivy-fs hook
pre-commit install
```

The hooks run automatically on `git commit`:
- **gitleaks** — blocks commits containing secrets (API keys, tokens, passwords)
- **check-added-large-files** — blocks files >500KB
- **ruff** — Python lint + format (auto-fixes)
- **oxlint** — TypeScript/JS lint
- **oxfmt** — TypeScript/JS format (auto-fixes)
- **trivy-fs** — only runs when `requirements.txt`/`pyproject.toml`/`uv.lock`/`package*.json`/`Dockerfile`
  change; blocks commits that introduce a HIGH/CRITICAL dependency CVE with a known fix

To run all hooks manually: `pre-commit run --all-files`

## Running locally

Open in VS Code and press **F5** → select **"Full Stack"**. Starts FastAPI on `localhost:8000` and Vite on `localhost:5173` with debuggers attached.

Alternatively:

```bash
cd api && uv run uvicorn main:app --reload --port 8000  # backend
cd web && npm run dev                                    # frontend
```

See [Local Development](/contributing/local-development/) for first-time setup and debugging tips.

## Commit messages

This repo uses [Conventional Commits](https://www.conventionalcommits.org/) — `release-please`
parses commit messages on every push to `main` to generate `CHANGELOG.md` and bump the version.
Use a `type:` prefix on every commit (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`).

### SQLite schema changes

Any PR that changes the embedded SQLite schema (new table, new column — anything that needs a
migration) must:

1. Add a migration to the `MIGRATIONS` list in `api/lib/db/migrations.py` (see that file's
   docstring for the framework). Self-hosters' existing data must upgrade automatically on next
   boot (`docker compose pull && docker compose up -d`) — there is no "wipe and re-bootstrap"
   fallback for ordinary schema changes; that path was a one-time exception for the pre-SQLite
   storage-engine swap.
2. Add a `BREAKING CHANGE:` footer to the commit message describing the schema change, even when
   it isn't an API break. This is the mechanism `release-please` uses to surface a commit under
   its own heading in `CHANGELOG.md` — without it, a schema-changing commit looks identical to
   any other `feat:`/`fix:` in the changelog, and self-hosters have no signal to read closely
   before upgrading. Example:

   ```
   feat: add archived flag to results

   BREAKING CHANGE: results table gains an `archived` column. Migration runs automatically
   on next boot — no manual action needed, called out here so self-hosters notice it in the
   changelog before upgrading.
   ```

## Pull requests

- Tests must pass: `cd api && uv run pytest tests/ -v`
- Keep scope small — one thing per PR
- Fill-out the PR template
