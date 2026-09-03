---
title: Local Development
description: Full-stack debugging with VS Code — FastAPI backend and React frontend simultaneously.
sidebar:
  order: 2
---

Full-stack debugging of the FastAPI backend and React frontend simultaneously in VS Code.

---

## Architecture

```
Browser (localhost:5173)
    ↓ /api/* requests
Vite dev server (proxy)
    ↓ forwards to
FastAPI / uvicorn (localhost:8000)
    ↓ reads/writes
AWS DynamoDB (real data, your AWS credentials)
```

`DEV_MODE=true` is set automatically by the launch config — this bypasses the CloudFront `x-origin-token` check so the API accepts requests from your local browser.

---

## Prerequisites

- [uv](https://docs.astral.sh/uv/) installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Node.js installed
- AWS credentials configured (`aws configure` or `~/.aws/credentials`)

### First-time: point local dev at AWS

`.vscode/launch.json` sets only `ENV` and `DEV_MODE`, and loads everything else from a
`.env` file in the repo root (`envFile`). That file is gitignored — create it yourself.

The app defaults to self-hosted (SQLite, local files, env secrets), so a local session
aimed at the dev AWS stack has to say so explicitly:

```bash
# .env — repo root, never committed
DB_BACKEND=dynamodb
STORAGE_BACKEND=s3
SECRETS_PROVIDER=ssm

AWS_REGION=eu-west-1
S3_BUCKET=<your-dev-bucket>
# (CLOUDFRONT_URL is no longer used by the app — media URLs are relative)
USERS_TABLE=boardsite-users-dev
GAMES_TABLE=boardsite-games-dev
RESULTS_TABLE=boardsite-results-dev
POSTS_TABLE=boardsite-posts-dev
RECS_TABLE=boardsite-recs-dev
REACTIONS_TABLE=boardsite-reactions-dev
NOTIFICATIONS_TABLE=boardsite-notifications-dev
SETTINGS_TABLE=boardsite-settings-dev
```

Without the first three, F5 starts against an embedded SQLite file instead of DynamoDB
and fails on the missing `/data` directory.

### First-time: create an admin user

```bash
cd api
DB_BACKEND=dynamodb uv run python3 scripts/create-user.py \
  --username admin \
  --display-name "Admin" \
  --role admin \
  --password yourpassword
```

The `DB_BACKEND=dynamodb` prefix is what sends the script to AWS rather than a local
SQLite file. The `task create-user` / `task users` targets set it for you.

---

## Starting the Debug Session

1. Open the repo root in VS Code.
2. Press **F5**.
3. Select **"Full Stack"** from the dropdown.

VS Code will:
- Run `uv sync` in `api/` (installs/updates Python deps)
- Run `npm install` in `web/` (installs/updates Node deps)
- Start FastAPI on `localhost:8000` with the Python debugger attached
- Start Vite on `localhost:5173` with the Node debugger attached
- Open Chrome at `http://localhost:5173` once Vite is ready

Both processes stop together when you press the red square or close VS Code.

---

## Setting Breakpoints

### Python (FastAPI backend)

Open any file in `api/routes/` or `api/lib/` and click in the gutter (left margin) to set a breakpoint.

**Example: trace a login request**

1. Open `api/routes/auth.py`
2. Set a breakpoint on the `get_user(body.username)` line inside `login`
3. In the browser, submit the login form
4. VS Code pauses — hover over `body` to inspect `username` and `password`
5. Step over (`F10`) to watch the password hash comparison
6. Resume (`F5`) to let the response complete

**Example: debug a database write**

1. Open `api/routes/results.py`
2. Set a breakpoint on the `put_result(result)` call in `create_result`
3. Log a result in the browser
4. Inspect the `result` dict before it's written — catches type errors and missing fields early

### TypeScript (React frontend)

Open any file in `web/src/` and set a breakpoint. VS Code's Chrome debugger maps source files via sourcemaps.

**Example: inspect API response data**

1. Open `web/src/hooks/useGames.ts`
2. Set a breakpoint inside the `useGames` query's `queryFn`
3. Navigate to the Catalog page in the browser
4. VS Code pauses — step out to see the resolved data

**Example: trace a form submission**

1. Open `web/src/components/LogResultDialog.tsx`
2. Set a breakpoint on the `mutate(...)` call
3. Submit the form
4. Inspect the payload before it's sent to the API

---

## Running Tests

Tests use an in-memory `FakeTable` (`api/tests/conftest.py`) standing in for the database — no real AWS calls, no data contamination.

```bash
cd api
uv run pytest tests/ -v          # all tests (takes a few minutes)
uv run pytest tests/ -v -k auth  # filter by name
uv run pytest tests/test_routes_results.py -v  # single file
```

---

## Common Workflows

### Add a new API route and test it locally

1. Create `api/routes/myroute.py`
2. Register it in `api/main.py`: `app.include_router(myroute.router, prefix="/api/myroute")`
3. Press F5 — uvicorn `--reload` picks up the change automatically (no restart needed)
4. Test via browser or curl:
   ```bash
   curl http://localhost:8000/api/myroute
   ```

### Inspect what's in DynamoDB

```bash
cd api
DB_BACKEND=dynamodb uv run python3 -c "
from lib.db.results import list_results
import json
print(json.dumps(list_results(), indent=2, default=str))
"
```

Without `DB_BACKEND=dynamodb` the snippet opens a local SQLite file instead — see the `.env` note above.

### Add a Python dependency

```bash
cd api
uv add some-package       # adds to pyproject.toml and syncs .venv
```

Then commit both `pyproject.toml` and `uv.lock`.

> **Note:** Also add the package to `requirements.txt` if it's needed in the Lambda (production). `requirements.txt` is used by `build.sh` for the Lambda zip — `pyproject.toml` is local dev only.

---

## Troubleshooting

**F5 does nothing / wrong config selected**
Select the "Full Stack" compound from the Run & Debug dropdown (the play button in the sidebar), not a single config.

**`uv sync` fails in preLaunchTask**
Run manually: `cd api && uv sync`. If it errors, check Python version: `uv python list`.

**Backend starts but login returns 503**
The app failed to fetch secrets from SSM at startup. Check:
- AWS credentials: `aws sts get-caller-identity`
- `AWS_REGION` in `.env` matches where the stack is deployed
- SSM params exist: `aws ssm get-parameter --name /boardsite/jwt-secret --region eu-west-1`

**Vite proxy returns 502 / ECONNREFUSED**
FastAPI isn't running yet. Check the "Debug Backend" terminal tab in VS Code for startup errors.

**Breakpoint not hit in Python**
`--reload` mode spawns a child process. The launch config has `"subProcess": true` which should handle this. If breakpoints still don't hit, stop and restart the debug session.

**Chrome doesn't open automatically**
Vite's `serverReadyAction` watches for the `Local:` URL in the terminal output. If it doesn't trigger, open `http://localhost:5173` manually.
