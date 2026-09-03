from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends

from lib.auth import AuthUser, require_auth
from lib.db.notifications import list_notifications_for_player
from lib.db.users import get_user, set_last_read_at

router = APIRouter()


@router.get("")
def list_notifications(user: Annotated[AuthUser, Depends(require_auth)]):
    items = list_notifications_for_player(user.sub)
    last_read_at = (get_user(user.sub) or {}).get("lastReadAt")
    unread_count = sum(1 for n in items if last_read_at is None or n["createdAt"] > last_read_at)
    return {"notifications": items, "unreadCount": unread_count}


@router.post("/read", status_code=204)
def mark_notifications_read(user: Annotated[AuthUser, Depends(require_auth)]):
    set_last_read_at(user.sub, datetime.now(timezone.utc).isoformat())
