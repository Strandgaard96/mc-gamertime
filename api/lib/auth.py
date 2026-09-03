from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional

from fastapi import Cookie, Depends, HTTPException
from jose import JWTError, jwt

from lib.db.users import get_user

_jwt_secret: Optional[str] = None

# bcrypt refuses passwords longer than 72 *bytes* — it raises ValueError rather
# than truncating, so anything that reaches hashpw/checkpw with a longer value
# blows up with a 500. Note this is bytes, not characters: 36 accented
# characters already exceed it.
MAX_PASSWORD_BYTES = 72


def password_within_bcrypt_limit(password: str) -> bool:
    return len(password.encode("utf-8")) <= MAX_PASSWORD_BYTES


def validate_password_length(password: str) -> str:
    """Pydantic validator body for every field that ends up in bcrypt."""
    if not password_within_bcrypt_limit(password):
        raise ValueError(
            f"password must be at most {MAX_PASSWORD_BYTES} bytes "
            "(accented and non-Latin characters count as more than one byte)"
        )
    return password


def set_jwt_secret(secret: str) -> None:
    global _jwt_secret
    _jwt_secret = secret


@dataclass
class AuthUser:
    sub: str
    role: str
    displayName: str
    tokenVersion: int = 0


def sign_token(user: AuthUser) -> str:
    payload = {
        "sub": user.sub,
        "role": user.role,
        "displayName": user.displayName,
        "tv": user.tokenVersion,
        "exp": int((datetime.now(timezone.utc) + timedelta(days=7)).timestamp()),
    }
    return jwt.encode(payload, _jwt_secret, algorithm="HS256")


def decode_token(token: str) -> AuthUser:
    payload = jwt.decode(token, _jwt_secret, algorithms=["HS256"])
    # Auth tokens carry no `purpose` claim. Reject anything that does (e.g. a
    # password-reset token signed with the same secret) so it can't be replayed
    # as a session cookie — mirrors decode_reset_token's purpose check.
    if payload.get("purpose") is not None:
        raise JWTError("Not an auth token")
    return AuthUser(
        sub=payload["sub"],
        role=payload["role"],
        displayName=payload["displayName"],
        tokenVersion=payload.get("tv", 0),
    )


def require_auth(token: Annotated[Optional[str], Cookie()] = None) -> AuthUser:
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    try:
        auth_user = decode_token(token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user = get_user(auth_user.sub)
    if user is None or user.get("tokenVersion", 0) != auth_user.tokenVersion:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return auth_user


def require_admin(user: Annotated[AuthUser, Depends(require_auth)]) -> AuthUser:
    # Re-read the role from the user record rather than trusting the JWT claim,
    # so a demoted admin loses access immediately even if their 7-day token still
    # says "admin". (require_auth already fetched+validated tokenVersion, but the
    # role claim itself is only as fresh as the last token mint.)
    current = get_user(user.sub)
    if current is None or current.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    return user


_RESET_PURPOSE = "pwreset"
_RESET_TTL_MINUTES = 15


def sign_reset_token(username: str, token_version: int) -> str:
    payload = {
        "sub": username,
        "purpose": _RESET_PURPOSE,
        "tv": token_version,
        "exp": int(
            (datetime.now(timezone.utc) + timedelta(minutes=_RESET_TTL_MINUTES)).timestamp()
        ),
    }
    return jwt.encode(payload, _jwt_secret, algorithm="HS256")


def decode_reset_token(token: str) -> tuple[str, int]:
    payload = jwt.decode(token, _jwt_secret, algorithms=["HS256"])
    if payload.get("purpose") != _RESET_PURPOSE:
        raise JWTError("Not a password-reset token")
    return payload["sub"], payload.get("tv", 0)
