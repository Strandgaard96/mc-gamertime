from __future__ import annotations

import os
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, field_validator

from lib import bgg as bgg_lib
from lib.auth import AuthUser, require_admin
from lib.db.settings import get_settings, put_settings

router = APIRouter()

_DEFAULT_DISPLAY_NAME = "MC GamerTime"


@router.get("/public")
def get_public_settings():
    settings = get_settings()
    return {"displayName": settings.get("displayName") or _DEFAULT_DISPLAY_NAME}


@router.get("")
def get_settings_route(_: Annotated[AuthUser, Depends(require_admin)]):
    settings = get_settings()
    return {
        "displayName": settings.get("displayName") or _DEFAULT_DISPLAY_NAME,
        "bggTokenSet": bool(settings.get("bggToken")),
        "appBaseUrl": settings.get("appBaseUrl"),
        "appBaseUrlEnvFallback": os.environ.get("APP_BASE_URL") or None,
    }


class UpdateSettingsBody(BaseModel):
    displayName: str | None = None
    bggToken: str | None = None
    appBaseUrl: str | None = None

    @field_validator("displayName")
    @classmethod
    def validate_display_name(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if not (1 <= len(v) <= 60):
            raise ValueError("must be 1-60 characters")
        return v

    @field_validator("bggToken")
    @classmethod
    def validate_bgg_token(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return v.strip() or None

    @field_validator("appBaseUrl")
    @classmethod
    def validate_app_base_url(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if not v:
            return None
        if not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("must start with http:// or https://")
        if not v.removeprefix("http://").removeprefix("https://"):
            raise ValueError("must include a host")
        return v.rstrip("/")


@router.put("")
def update_settings_route(body: UpdateSettingsBody, _: Annotated[AuthUser, Depends(require_admin)]):
    existing = get_settings()
    updated = {k: v for k, v in existing.items() if k != "pk"}
    for key, value in body.model_dump(exclude_unset=True).items():
        if value is None:
            updated.pop(key, None)
        else:
            updated[key] = value
    put_settings({"pk": "instance", **updated})
    bgg_lib.refresh_token_from_db()
    return {
        "displayName": updated.get("displayName") or _DEFAULT_DISPLAY_NAME,
        "bggTokenSet": bool(updated.get("bggToken")),
        "appBaseUrl": updated.get("appBaseUrl"),
        "appBaseUrlEnvFallback": os.environ.get("APP_BASE_URL") or None,
    }
