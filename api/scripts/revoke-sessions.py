#!/usr/bin/env python3
"""Invalidate every active session for a boardsite user by bumping tokenVersion.

cd api && uv run python3 scripts/revoke-sessions.py --username alice [--env dev]
"""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def main():
    parser = argparse.ArgumentParser(description="Revoke all active sessions for a boardsite user")
    parser.add_argument("--username", required=True)
    parser.add_argument("--env", choices=["prod", "dev"], default="prod")
    args = parser.parse_args()

    if args.env == "dev":
        os.environ.setdefault("USERS_TABLE", "boardsite-users-dev")

    from lib.db.users import get_user, put_user  # deferred: --env must set USERS_TABLE first

    user = get_user(args.username)
    if not user:
        print(f"User '{args.username}' not found.")
        sys.exit(1)

    user["tokenVersion"] = user.get("tokenVersion", 0) + 1
    put_user(user)
    print(f"Revoked sessions for '{args.username}' (tokenVersion now {user['tokenVersion']}).")


if __name__ == "__main__":
    main()
