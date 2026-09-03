from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, field_validator
from ulid import ULID

from lib.auth import AuthUser, require_auth
from lib.db.reactions import (
    delete_reaction,
    find_reaction,
    get_reaction,
    list_reactions,
    put_reaction,
)
from lib.db.results import get_result
from lib.rate_limit import limiter

router = APIRouter()
comments_router = APIRouter()

REACTION_EMOJIS = {"👍", "❤️", "😂", "😮", "🎉", "🔥"}


class ToggleReactionBody(BaseModel):
    sessionPk: str
    emoji: str

    @field_validator("emoji")
    @classmethod
    def emoji_in_palette(cls, v: str) -> str:
        if v not in REACTION_EMOJIS:
            raise ValueError("emoji must be one of the supported reactions")
        return v


class CreateCommentBody(BaseModel):
    sessionPk: str
    text: str

    @field_validator("text")
    @classmethod
    def text_length(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("text must not be empty")
        if len(v) > 500:
            raise ValueError("text must be 500 characters or fewer")
        return v


@router.get("")
def list_reactions_route(_: Annotated[AuthUser, Depends(require_auth)]):
    return list_reactions()


@router.post("/toggle")
@limiter.limit("60/minute")
def toggle_reaction(
    body: ToggleReactionBody,
    request: Request,
    response: Response,
    user: Annotated[AuthUser, Depends(require_auth)],
):
    if not get_result(body.sessionPk):
        raise HTTPException(status_code=404, detail="Session not found")

    # Scan-then-write: a rapid double-tap could see "absent" twice and insert
    # twice. Accepted at this scale; client disables the button while pending.
    existing = find_reaction(body.sessionPk, body.emoji, user.sub)

    if existing:
        delete_reaction(existing["pk"])
        return {"action": "removed", "item": None}

    item = {
        "pk": str(ULID()),
        "type": "reaction",
        "sessionPk": body.sessionPk,
        "emoji": body.emoji,
        "userId": user.sub,
        "userName": user.displayName,
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }
    put_reaction(item)
    return {"action": "added", "item": item}


@comments_router.post("", status_code=201)
@limiter.limit("30/minute")
def create_comment(
    body: CreateCommentBody,
    request: Request,
    response: Response,
    user: Annotated[AuthUser, Depends(require_auth)],
):
    if not get_result(body.sessionPk):
        raise HTTPException(status_code=404, detail="Session not found")

    item = {
        "pk": str(ULID()),
        "type": "comment",
        "sessionPk": body.sessionPk,
        "authorId": user.sub,
        "authorName": user.displayName,
        "text": body.text,
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }
    put_reaction(item)
    return item


@comments_router.delete("/{comment_id}", status_code=204)
def delete_comment(comment_id: str, user: Annotated[AuthUser, Depends(require_auth)]):
    # Return an identical 404 for missing, wrong-type, and not-owned so a
    # non-owner can't distinguish "comment exists" from "comment doesn't exist"
    # (deny without confirming existence — CWE-639/209).
    existing = get_reaction(comment_id)
    if (
        not existing
        or existing.get("type") != "comment"
        or (existing["authorId"] != user.sub and user.role != "admin")
    ):
        raise HTTPException(status_code=404, detail="Comment not found")

    delete_reaction(comment_id)
