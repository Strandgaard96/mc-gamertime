import logging
import os
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field
from ulid import ULID

from lib.auth import AuthUser, require_auth
from lib.db.reactions import (
    delete_reaction,
    find_photo_by_key,
    get_reaction,
    list_session_photos,
    put_reaction,
)
from lib.db.results import get_result
from lib.rate_limit import limiter
from lib.storage import (
    MAX_PHOTO_BYTES,
    PHOTO_CONTENT_TYPES,
    PHOTO_KEY_RE,
    PHOTO_PREFIX,
    build_upload,
    get_object_base_url,
    make_s3_client,
)

router = APIRouter()
logger = logging.getLogger(__name__)

MAX_PHOTOS_PER_SESSION = 6

_s3 = make_s3_client()
_BUCKET = os.environ.get("S3_BUCKET", "")
_OBJECT_BASE_URL = get_object_base_url()


class UploadPhotoBody(BaseModel):
    sessionPk: str
    contentType: str
    # Bound into the upload URL (S3 ContentLength / the /storage proxy token),
    # so the PUT must send exactly this many bytes.
    contentLength: int = Field(ge=1, le=MAX_PHOTO_BYTES)


class CreatePhotoBody(BaseModel):
    sessionPk: str
    key: str


def _require_session_with_room(session_pk: str) -> None:
    if not get_result(session_pk):
        raise HTTPException(status_code=404, detail="Session not found")
    # Scan-then-write: two concurrent uploads could both see 5 and land a 7th.
    # Accepted at this scale, same as reactions.
    if len(list_session_photos(session_pk)) >= MAX_PHOTOS_PER_SESSION:
        raise HTTPException(status_code=409, detail="Photo limit reached for this session")


def _delete_object(key: str) -> None:
    try:
        _s3.delete_object(Bucket=_BUCKET, Key=key)
    except Exception:
        # The row is the source of truth; an orphaned object is only storage.
        logger.exception("Failed to delete photo object %s", key)


def delete_session_photos(session_pk: str) -> None:
    """Remove every photo row and object for a session (result delete cascade)."""
    for photo in list_session_photos(session_pk):
        delete_reaction(photo["pk"])
        _delete_object(photo["key"])


@router.post("/upload")
@limiter.limit("20/minute")
def request_photo_upload(
    body: UploadPhotoBody,
    request: Request,
    response: Response,
    _: Annotated[AuthUser, Depends(require_auth)],
):
    if body.contentType not in PHOTO_CONTENT_TYPES:
        raise HTTPException(status_code=422, detail="Unsupported content type")
    _require_session_with_room(body.sessionPk)
    upload_url, image_url, key = build_upload(
        _s3, _BUCKET, _OBJECT_BASE_URL, PHOTO_PREFIX, body.contentType, body.contentLength
    )
    return {"uploadUrl": upload_url, "imageUrl": image_url, "key": key}


@router.post("", status_code=201)
@limiter.limit("20/minute")
def create_photo(
    body: CreatePhotoBody,
    request: Request,
    response: Response,
    user: Annotated[AuthUser, Depends(require_auth)],
):
    if not PHOTO_KEY_RE.match(body.key):
        raise HTTPException(status_code=422, detail="Invalid photo key")
    _require_session_with_room(body.sessionPk)
    # Not verified: that the object exists, or that this key was issued for this
    # session. ULID keys are unguessable and a broken row is deletable by its
    # owner or an admin.
    if find_photo_by_key(body.key):
        raise HTTPException(status_code=409, detail="Photo already registered")

    item = {
        "pk": str(ULID()),
        "type": "photo",
        "sessionPk": body.sessionPk,
        "key": body.key,
        "imageUrl": f"{_OBJECT_BASE_URL}/{body.key}",
        "uploaderId": user.sub,
        "uploaderName": user.displayName,
        "createdAt": datetime.now(UTC).isoformat(),
    }
    put_reaction(item)
    return item


@router.delete("/{photo_id}", status_code=204)
def delete_photo(photo_id: str, user: Annotated[AuthUser, Depends(require_auth)]):
    # Identical 404 for missing, wrong-type, and not-owned (see delete_comment).
    existing = get_reaction(photo_id)
    if (
        not existing
        or existing.get("type") != "photo"
        or (existing["uploaderId"] != user.sub and user.role != "admin")
    ):
        raise HTTPException(status_code=404, detail="Photo not found")
    delete_reaction(photo_id)
    _delete_object(existing["key"])
