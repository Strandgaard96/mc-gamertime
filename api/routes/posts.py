import os
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from ulid import ULID

from lib.auth import AuthUser, require_admin, require_auth
from lib.db.posts import delete_post, get_post, list_posts, put_post
from lib.storage import EXT_BY_CONTENT_TYPE, build_upload_url, get_object_base_url, make_s3_client

router = APIRouter()

_CLEARABLE_POST_FIELDS = {"sessionPk", "gameName", "gamePk"}

_s3 = make_s3_client()
_BUCKET = os.environ.get("S3_BUCKET", "")
_OBJECT_BASE_URL = get_object_base_url()


class CreatePostBody(BaseModel):
    title: str
    content: str
    sessionPk: str | None = None
    gameName: str | None = None
    gamePk: str | None = None

    @field_validator("title", "content")
    @classmethod
    def non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("must not be empty")
        return v.strip()


class UpdatePostBody(BaseModel):
    title: str | None = None
    content: str | None = None
    sessionPk: str | None = None
    gameName: str | None = None
    gamePk: str | None = None


class UploadImageBody(BaseModel):
    filename: str = "image.bin"  # accepted for client compat; ignored — ext comes from contentType
    contentType: str = "application/octet-stream"


def generate_upload_url(content_type: str) -> tuple[str, str]:
    return build_upload_url(_s3, _BUCKET, _OBJECT_BASE_URL, "blog-images", content_type)


@router.get("")
def list_posts_route(_: Annotated[AuthUser, Depends(require_auth)]):
    return list_posts()


@router.post("/upload")
def upload_image(body: UploadImageBody, _: Annotated[AuthUser, Depends(require_admin)]):
    # NOTE: declared before /{post_id} to prevent route shadowing
    if body.contentType not in EXT_BY_CONTENT_TYPE:
        raise HTTPException(status_code=422, detail="Unsupported content type")
    upload_url, image_url = generate_upload_url(body.contentType)
    return {"uploadUrl": upload_url, "imageUrl": image_url}


@router.get("/{post_id}")
def get_post_route(post_id: str, _: Annotated[AuthUser, Depends(require_auth)]):
    item = get_post(post_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return item


@router.post("", status_code=201)
def create_post(body: CreatePostBody, user: Annotated[AuthUser, Depends(require_admin)]):
    post_id = str(ULID())
    post = {
        "pk": post_id,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "authorName": user.displayName,
        **body.model_dump(exclude_none=True),
    }
    put_post(post)
    return post


@router.put("/{post_id}")
def update_post(post_id: str, body: UpdatePostBody, _: Annotated[AuthUser, Depends(require_admin)]):
    existing = get_post(post_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Post not found")
    updated = {**existing}
    # exclude_unset (not exclude_none) so an explicit null clears the field
    for key, value in body.model_dump(exclude_unset=True).items():
        if value is None:
            if key not in _CLEARABLE_POST_FIELDS:
                raise HTTPException(status_code=422, detail=f"{key} cannot be null")
            updated.pop(key, None)
        else:
            updated[key] = value
    put_post(updated)
    return updated


@router.delete("/{post_id}", status_code=204)
def delete_post_route(post_id: str, _: Annotated[AuthUser, Depends(require_admin)]):
    existing = get_post(post_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Post not found")
    delete_post(post_id)
