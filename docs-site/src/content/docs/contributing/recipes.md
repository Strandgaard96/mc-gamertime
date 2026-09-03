---
title: Feature Recipes
description: Concrete step-by-step recipes for common feature types, plus common mistakes to avoid.
sidebar:
  order: 4
---

Concrete recipes for common feature types. Each recipe lists every file to touch, in order, with the exact pattern to follow.

---

## Recipe 1: Add an endpoint to an existing route

**Example:** add `GET /api/results/{pk}` to the results route (it doesn't exist yet — only list/create/update/delete do).

**Files to touch:** 1

**`api/routes/results.py`** — the DB function `get_result` already exists in `api/lib/db/results.py` (it's used internally by the update/delete handlers) and is already imported. Just add the route:

```python
@router.get("/{result_id}")
def get_result_route(result_id: str, _: Annotated[AuthUser, Depends(require_auth)]):
    item = get_result(result_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Result not found")
    return item
```

**Route ordering matters:** FastAPI matches routes top-to-bottom. If you have `GET /upload` and `GET /{id}`, declare `/upload` first or it gets swallowed by the param route. See `api/routes/posts.py` for the real example (`POST /upload` is declared before `GET /{post_id}`).

---

## Recipe 2: Add a new write operation (mutation)

**Example:** let admin mark a result as "featured".

**Files to touch:** 4 backend + 3 frontend

**Backend — `api/routes/results.py`:**

```python
class FeaturedBody(BaseModel):
    featured: bool

@router.put("/{result_id}/featured", status_code=200)
def set_featured(result_id: str, body: FeaturedBody, _: Annotated[AuthUser, Depends(require_admin)]):
    existing = get_result(result_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Result not found")
    updated = {**existing, "featured": body.featured}
    put_result(updated)
    return updated
```

**Frontend — `web/src/lib/api.ts`:** add the function

```typescript
export function setResultFeatured(id: string, featured: boolean): Promise<Result> {
  return apiFetch(`/results/${id}/featured`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ featured }),
  })
}
```

**Frontend — `web/src/hooks/useResults.ts`:** add the mutation hook

```typescript
import { setResultFeatured } from '../lib/api'

export function useSetResultFeatured() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, featured }: { id: string; featured: boolean }) =>
      setResultFeatured(id, featured),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['results'] })
      toast.success('Updated')
    },
    onError: () => toast.error('Failed to update'),
  })
}
```

**Frontend — page component:** use the hook

```typescript
const setFeatured = useSetResultFeatured()
// later in JSX:
<button onClick={() => setFeatured.mutate({ id: r.pk, featured: true })}>
  Feature
</button>
```

**Invalidation rule:** invalidate every query key that shows data this mutation changes. Results affect stats (leaderboard), so invalidate both `['results']` and `['stats']`.

---

## Recipe 3: Add a new read-only page

**Example:** a `/history` page showing results grouped by month.

**Files to touch:** 3

**1. `web/src/pages/HistoryPage.tsx`** — create the page

```tsx
import { useResults } from '../hooks/useResults'
import { PageTransition } from '../components/PageTransition'

export default function HistoryPage() {
  const { data: results = [], isLoading } = useResults()

  if (isLoading) return <p className="p-6 text-muted-foreground">Loading…</p>

  return (
    <PageTransition>
    <div className="max-w-xl mx-auto p-4 md:p-6">
      <h1 className="text-2xl font-display font-bold mb-6">History</h1>
      {/* render results */}
    </div>
    </PageTransition>
  )
}
```

Always wrap the return in `<PageTransition>` — it's the fade animation between routes. Without it the page appears without the transition.

**2. `web/src/App.tsx`** — add import + route

```typescript
// with other imports at the top
import HistoryPage from './pages/HistoryPage'
```

```tsx
// inside the authenticated Routes block
<Route path="/history" element={<HistoryPage />} />
```

**3. `web/src/App.tsx`** — optionally add a nav item

```typescript
// in NAV_ITEMS, add:
{ to: '/history', label: 'History', icon: <Clock size={18} /> },
```

No backend changes needed if you're reusing existing data (results, posts, etc.) that's already cached.

---

## Recipe 4: Add a completely new feature (new DynamoDB table)

**Example:** game ratings — users rate games 1-5 stars.

This is the full end-to-end. Do it in this order.

**Step 1 — Backend DB layer: `api/lib/db/ratings.py`** (new file)

```python
from __future__ import annotations
import lib.db.base as _db

def list_ratings() -> list[dict]:
    return _db.paginated_scan(_db.tables["ratings"])

def get_rating(pk: str) -> dict | None:
    return _db.tables["ratings"].get_item(Key={"pk": pk}).get("Item")

def put_rating(item: dict) -> None:
    _db.tables["ratings"].put_item(Item=_db._floats_to_decimal(item))

def delete_rating(pk: str) -> None:
    _db.tables["ratings"].delete_item(Key={"pk": pk})
```

**Step 2 — Register the table in both backends**

```python
# api/lib/db/base.py, in _make_tables():
"ratings": DynamoTable(dynamo.Table(os.environ.get("RATINGS_TABLE", "boardsite-ratings"))),
```

```python
# api/lib/db/sqlite_backend.py, in _TABLE_NAMES:
"ratings",
```

The SQLite table is created on next boot from that tuple — no migration needed.

**Step 3 — Backend route: `api/routes/ratings.py`** (new file)

```python
from datetime import datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from ulid import ULID
from lib.auth import AuthUser, require_auth
from lib.db.ratings import list_ratings, get_rating, put_rating

router = APIRouter()

class RatingBody(BaseModel):
    gameId: str
    stars: int

    @field_validator("stars")
    @classmethod
    def valid_stars(cls, v: int) -> int:
        if not 1 <= v <= 5:
            raise ValueError("stars must be 1-5")
        return v

@router.get("")
def get_ratings(_: Annotated[AuthUser, Depends(require_auth)]):
    return list_ratings()

@router.post("", status_code=201)
def create_rating(body: RatingBody, user: Annotated[AuthUser, Depends(require_auth)]):
    rating = {
        "pk": str(ULID()),
        "gameId": body.gameId,
        "stars": body.stars,
        "userId": user.sub,
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }
    put_rating(rating)
    return rating
```

**Step 4 — `api/main.py`** — register the router

```python
from routes import auth, games, players, posts, recommended, results, stats, users, ratings
# ...
app.include_router(ratings.router, prefix="/api/ratings")
```

**Step 5 — Infra** — three files, following the existing tables:

- `infra/variables.tf`: a `ratings_table_name` variable (default `boardsite-ratings`)
- `infra/dynamodb.tf`: add `ratings = var.ratings_table_name` to `local.dynamo_tables` (the
  `for_each` creates the table with PITR and deletion protection; the Lambda IAM policy
  already covers every table in that map)
- `infra/lambda.tf`: add `RATINGS_TABLE` to the Lambda environment block

**Step 6 — Tests** — nothing to register: `fake_db` builds one fake table per `_TABLE_NAMES`
entry, so `fake_db["ratings"]` works as soon as Step 2 is done.

**Step 7 — Frontend types: `web/src/lib/types.ts`**

```typescript
export interface Rating {
  pk: string
  gameId: string
  stars: number
  userId: string
  createdAt: string
}
```

**Step 8 — Frontend API: `web/src/lib/api.ts`**

```typescript
import type { ..., Rating } from './types'

export function getRatings(): Promise<Rating[]> {
  return apiFetch('/ratings')
}

export function createRating(data: { gameId: string; stars: number }): Promise<Rating> {
  return apiFetch('/ratings', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
}
```

**Step 9 — Frontend hook: `web/src/hooks/useRatings.ts`** (new file)

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { getRatings, createRating } from '../lib/api'

export function useRatings() {
  return useQuery({ queryKey: ['ratings'], queryFn: getRatings })
}

export function useCreateRating() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: createRating,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['ratings'] })
      toast.success('Rating saved')
    },
    onError: () => toast.error('Failed to save rating'),
  })
}
```

**Step 10 — Use in a page component** — import `useRatings` and `useCreateRating`, render.

---

## Recipe 5: Add an admin-only feature

Two guards needed — one on each side.

**Backend:** use `require_admin` dependency instead of `require_auth`:

```python
@router.delete("/{id}", status_code=204)
def delete_thing(id: str, _: Annotated[AuthUser, Depends(require_admin)]):
    ...
```

`require_admin` automatically calls `require_auth` first — you don't need both.

**Frontend:** check `user?.role === 'admin'` before rendering the UI:

```tsx
const { user } = useAuth()

{user?.role === 'admin' && (
  <Button onClick={handleDelete}>Delete</Button>
)}
```

For entire pages: gate the route in `App.tsx`:

```tsx
{user.role === 'admin' && <Route path="/admin/thing" element={<ThingAdminPage />} />}
```

Non-admins who navigate to `/admin/thing` directly get no route match → falls through to the catch-all (no-op in the authenticated block, since there's no redirect). If you want a hard redirect, add one.

---

## Recipe 6: Write tests for a new endpoint

Tests live in `api/tests/test_routes_<name>.py`. The test infrastructure (`conftest.py`) gives you three fixtures automatically:

- **`fake_db`** — in-memory DynamoDB substitute. Call `fake_db["tablename"].seed({...})` to pre-populate.
- **`authed_client`** — factory that returns a `TestClient` with a real signed JWT cookie. Call `authed_client("admin")` or `authed_client("readonly")`.
- **`ORIGIN`** — the `x-origin-token` header dict. Every request needs `headers=ORIGIN`.

**Template for a new test file:**

```python
from fastapi.testclient import TestClient
from main import app
from tests.conftest import ORIGIN

# Seed helper — always include all required fields + createdAt
def _seed_rating(fake_db, pk: str = "01RATING"):
    fake_db["ratings"].seed({
        "pk": pk,
        "gameId": "01GAME",
        "stars": 4,
        "userId": "alice",
        "createdAt": "2026-01-01T00:00:00Z",
    })

# Test list (authenticated)
def test_list_ratings(authed_client, fake_db):
    _seed_rating(fake_db)
    c = authed_client("readonly")
    resp = c.get("/api/ratings", headers=ORIGIN)
    assert resp.status_code == 200
    assert len(resp.json()) == 1

# Test create (authenticated)
def test_create_rating(authed_client, fake_db):
    c = authed_client("readonly")
    resp = c.post("/api/ratings", json={"gameId": "01GAME", "stars": 5}, headers=ORIGIN)
    assert resp.status_code == 201
    assert resp.json()["stars"] == 5

# Test auth guard (unauthenticated)
def test_list_ratings_unauthenticated(fake_db):
    c = TestClient(app, raise_server_exceptions=False)
    resp = c.get("/api/ratings", headers=ORIGIN)
    assert resp.status_code == 401

# Test validation
def test_create_rating_invalid_stars(authed_client, fake_db):
    c = authed_client("readonly")
    resp = c.post("/api/ratings", json={"gameId": "01GAME", "stars": 6}, headers=ORIGIN)
    assert resp.status_code == 422
```

**TDD order (required by our workflow):**
1. Write tests → run → confirm they FAIL
2. Write implementation → run → confirm they PASS
3. Run full suite: `cd api && uv run pytest tests/ -q`

---

## Recipe 7: Add a field to an existing data type

**Example:** add `notes: str` to Result.

**Backend (3 changes):**

1. `api/routes/results.py` — add `notes` to the request body model:
```python
class AddResultBody(BaseModel):
    ...
    notes: str | None = None
```
The field is optional (`None`) so existing items without it don't break. It's included in `model_dump()` automatically and stored in DynamoDB.

2. No change to `api/lib/db/results.py` — the DB layer stores whatever dict you give it.

3. Tests — add a test that creates a result with `notes` and reads it back.

**Frontend (2 changes):**

1. `web/src/lib/types.ts` — add to the `Result` interface:
```typescript
export interface Result {
  ...
  notes?: string
}
```

2. Anywhere you create/edit results — add the field to the form and include it in the API call payload.

No migration needed on either backend: DynamoDB is schemaless and the SQLite backend stores each item as a JSON blob. Old items without `notes` return the field as missing/undefined, which TypeScript's `?` optional handles fine.

---

## Common Mistakes

**Forgot `createdAt` on a new item**
Items without `createdAt` are silently excluded from the `type-index` GSI. Always set it:
```python
"createdAt": datetime.now(timezone.utc).isoformat(),
```

**Float in DynamoDB payload**
DynamoDB rejects Python `float`. The `_floats_to_decimal()` call in every `put_*` function handles this, but only if you call `put_result(item)` — not if you call `_db.tables["results"].put_item(Item=item)` directly. Always go through the db module functions.

**Forgot to invalidate the right query keys**
If a mutation changes data shown on multiple pages, invalidate all relevant keys. Results affect stats: invalidate both `['results']` and `['stats']`. Rec edits affect the detail cache: invalidating `['recommended']` also clears `['recommended', id]` by prefix match.

**Added route in wrong block in `App.tsx`**
There are two route blocks: an unauthenticated one and an authenticated one. Public pages need to be in both. Authenticated-only pages go only in the authenticated block.

**Used `apiFetch` for a public endpoint**
`apiFetch` triggers 401 auto-logout if the server returns 401. Public endpoints that legitimately work without a cookie should use bare `fetch` and handle errors manually, like `getRecommended()` does in `api.ts`.

**Skipped `raise_server_exceptions=False` in tests**
Without this, a 404 or 422 from FastAPI raises an exception in the test instead of returning a response. Always use `TestClient(app, raise_server_exceptions=False)` for tests that expect error responses. The `authed_client` fixture already includes this.
