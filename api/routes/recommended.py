import os
import re
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException
from pydantic import BaseModel, field_validator
from ulid import ULID

from lib.auth import AuthUser, require_admin, require_auth
from lib.db.games import get_game
from lib.db.recs import delete_rec, get_rec, list_recs, put_rec

router = APIRouter()

# Cloud landing page shows recommended games to anonymous visitors; selfhost
# sets this to "false" so nothing is reachable without logging in.
PUBLIC_RECOMMENDED_ENABLED = os.environ.get("PUBLIC_RECOMMENDED_ENABLED", "false") == "true"

_BGG_FIELDS = ("minPlayers", "maxPlayers", "playTime", "weight", "yearPublished")

_CLEARABLE_REC_FIELDS = {"bestFor", "content"}


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return re.sub(r"-+", "-", slug)


class CreateRecommendedBody(BaseModel):
    gamePk: str
    blurb: str
    tags: list[str] = []
    bestFor: str | None = None
    order: int = 0

    @field_validator("gamePk", "blurb")
    @classmethod
    def non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("must not be empty")
        return v.strip()


class UpdateRecommendedBody(BaseModel):
    blurb: str | None = None
    tags: list[str] | None = None
    bestFor: str | None = None
    order: int | None = None
    content: str | None = None

    @field_validator("blurb")
    @classmethod
    def non_empty_blurb(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("must not be empty")
        return v.strip() if v is not None else v


@router.get("")
def list_recommended(token: Annotated[str | None, Cookie()] = None):
    if not PUBLIC_RECOMMENDED_ENABLED:
        require_auth(token)
    items = list_recs()
    result = []
    for item in sorted(items, key=lambda r: r.get("order", 0)):
        rec = {k: v for k, v in item.items() if k != "content"}
        rec["hasPost"] = bool(item.get("content"))
        if "slug" not in rec:
            rec["slug"] = _slugify(item.get("gameName", ""))
        result.append(rec)
    return result


@router.get("/{rec_id}")
def get_recommended(rec_id: str, token: Annotated[str | None, Cookie()] = None):
    if not PUBLIC_RECOMMENDED_ENABLED:
        require_auth(token)
    item = get_rec(rec_id)
    if item is None:
        # Slug fallback scans all recs on a pk miss — fine at current catalog scale.
        all_items = list_recs()
        item = next(
            (r for r in all_items if (r.get("slug") or _slugify(r.get("gameName", ""))) == rec_id),
            None,
        )
    if item is None:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    missing = [k for k in _BGG_FIELDS if k not in item]
    if missing and (game_pk := item.get("gamePk")):
        game = get_game(game_pk)
        if game:
            item = {**item, **{k: game[k] for k in missing if k in game}}
    return item


@router.post("", status_code=201)
def create_recommended(body: CreateRecommendedBody, _: Annotated[AuthUser, Depends(require_admin)]):
    game = get_game(body.gamePk)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    game_name = game.get("name", "")
    rec = {
        "pk": str(ULID()),
        "gameName": game_name,
        "slug": _slugify(game_name),
        "imageUrl": game.get("imageUrl", ""),
        "createdAt": datetime.now(UTC).isoformat(),
        **{k: game[k] for k in _BGG_FIELDS if k in game},
        **body.model_dump(),
    }
    put_rec(rec)
    return rec


@router.put("/{rec_id}", status_code=200)
def update_recommended(
    rec_id: str, body: UpdateRecommendedBody, _: Annotated[AuthUser, Depends(require_admin)]
):
    existing = get_rec(rec_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    updated = {**existing}
    # exclude_unset (not exclude_none) so an explicit null clears the field
    for key, value in body.model_dump(exclude_unset=True).items():
        if value is None:
            if key not in _CLEARABLE_REC_FIELDS:
                raise HTTPException(status_code=422, detail=f"{key} cannot be null")
            updated.pop(key, None)
        else:
            updated[key] = value
    put_rec(updated)
    return updated


@router.delete("/{rec_id}", status_code=204)
def delete_recommended(rec_id: str, _: Annotated[AuthUser, Depends(require_admin)]):
    if not get_rec(rec_id):
        raise HTTPException(status_code=404, detail="Recommendation not found")
    delete_rec(rec_id)
