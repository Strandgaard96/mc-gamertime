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

Requires [uv](https://docs.astral.sh/uv/) installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`). Tests use an in-memory fake table — no AWS credentials or running stack needed. The full suite takes a few minutes.

## First-time setup

Install [pre-commit](https://pre-commit.com/) and activate the hooks:

```bash
uv tool install pre-commit
cd web && npm install   # so the oxlint/oxfmt hooks find node_modules
cd ..
pre-commit install
```

Some hooks need tools on your `PATH`: [trivy](https://trivy.dev/latest/getting-started/installation/)
and [terraform](https://developer.hashicorp.com/terraform/install); the hadolint and
shellcheck hooks run in Docker.

The hooks run automatically on `git commit`:
- **gitleaks** — blocks commits containing secrets
- **ruff** (Python) and **oxlint** / **oxfmt** (TypeScript) — lint + format, auto-fixing
- **trivy-fs** — blocks a HIGH/CRITICAL dependency CVE with a known fix; runs only when a
  dependency manifest or the `Dockerfile` changes
- **actionlint**, **terraform_fmt** / **terraform_validate**, **hadolint**, **shellcheck** — lint
  workflows, Terraform, the Dockerfile, and shell scripts
- file hygiene — large files (>500KB), merge-conflict markers, trailing whitespace, YAML/JSON/TOML syntax

To run all hooks manually: `pre-commit run --all-files`

## Running locally

Open in VS Code and press **F5** → select **"Full Stack"**. Starts FastAPI on `localhost:8000` and Vite on `localhost:5173` with debuggers attached.

Alternatively, after creating the repo-root `.env` described in
[Local Development](/contributing/local-development/) (without it the API starts in
self-hosted SQLite mode and fails on the missing `/data` directory):

```bash
cd api && set -a && . ../.env && set +a && uv run uvicorn main:app --reload --port 8000  # backend
cd web && npm run dev                                                                    # frontend
```

See [Local Development](/contributing/local-development/) for first-time setup and debugging tips.

## Commit messages

This repo uses [Conventional Commits](https://www.conventionalcommits.org/) — `release-please`
parses commit messages on every push to `main` to generate `CHANGELOG.md` and bump the version.
Use a `type:` prefix on every commit (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`).

### SQLite schema changes

The self-hosted SQLite backend stores each item as a JSON blob (`pk`, `data`), so adding a
field to an existing type needs no migration, and a new table only needs its name added to
`_TABLE_NAMES` in `api/lib/db/sqlite_backend.py` (it is created on next boot). See
[Feature Recipes](/contributing/recipes/#recipe-4-add-a-completely-new-feature-new-dynamodb-table).

Anything beyond that — a new index, reshaping stored data — is a migration, and the PR must:

1. Add it to the `MIGRATIONS` list in `api/lib/db/migrations.py` (see that file's docstring).
   Self-hosters' existing data must upgrade automatically on next boot.
2. Add a `BREAKING CHANGE:` footer to the commit message, even when it isn't an API break.
   `release-please` surfaces such commits under their own heading in `CHANGELOG.md`, which is
   the only signal self-hosters get to read closely before upgrading. Example:

   ```
   feat: index results by gameId

   BREAKING CHANGE: adds an index on results.gameId. Migration runs automatically on next
   boot — no manual action needed, called out so self-hosters notice it before upgrading.
   ```

## Pull requests

- Tests must pass: `cd api && uv run pytest tests/ -v`
- Keep scope small — one thing per PR
- Fill-out the PR template
