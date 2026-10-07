---
title: Contributing
description: How to run tests and submit pull requests.
sidebar:
  order: 1
---

## Running checks

```bash
task check            # API + web + infra checks, then every git hook on all files
task check:api        # ruff lint + format check, ty, pytest + coverage floor
task check:web        # tsc, oxlint, oxfmt check, vitest + coverage
task check:infra      # terraform fmt check + validate
```

`task check` runs the same lint, type-check, test and Terraform commands as CI, so it is
the local gate before a PR (hadolint, shellcheck and Trivy run in CI only). It needs
[uv](https://docs.astral.sh/uv/) (`curl -LsSf https://astral.sh/uv/install.sh | sh`),
[Task](https://taskfile.dev/installation/),
[Terraform](https://developer.hashicorp.com/terraform/install) and `npm ci` in `web/`. Tests
use an in-memory fake table, so no AWS credentials or running stack are needed.

## First-time setup

Install [prek](https://prek.j178.dev/) (a drop-in, single-binary replacement for
pre-commit that reads the same `.pre-commit-config.yaml`; plain `pre-commit` works too) and
activate the hooks:

```bash
uv tool install prek
cd web && npm install   # so the oxlint/oxfmt hooks find node_modules
cd ..
prek install
```

The hooks are the fast subset and run automatically on `git commit`:
- **gitleaks** — blocks commits containing secrets
- **ruff** + **ty** (Python) and **oxlint** / **oxfmt** (TypeScript) — lint, type-check and
  format, auto-fixing where possible
- **zizmor** — audits the GitHub Actions workflows (unpinned actions, injection, permissions)
- **actionlint**, **terraform_fmt** — lint workflows and format Terraform
- file hygiene — large files (>500KB), merge-conflict markers, trailing whitespace, YAML/JSON/TOML syntax

To run all hooks manually: `prek run --all-files` (`task check` does this too).

Slower checks run in CI only: hadolint (Dockerfile) and shellcheck in the `Lint` job,
`terraform validate` in the `Terraform` job (and `task check:infra`), and Trivy. Trivy is
report-only on PRs (findings go to the Security tab), blocking in `publish.yml` before any
image is pushed, and blocking in the weekly `security-scan.yml` (image + lockfiles).

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

- `task check` must pass
- Keep scope small — one thing per PR
- Fill-out the PR template
