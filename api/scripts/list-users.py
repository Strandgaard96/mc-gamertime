#!/usr/bin/env python3
"""List all boardsite users.

cd api && uv run python3 scripts/list-users.py [--env dev]
"""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def main():
    parser = argparse.ArgumentParser(description="List boardsite users")
    parser.add_argument("--env", choices=["prod", "dev"], default="prod")
    args = parser.parse_args()

    if args.env == "dev":
        os.environ.setdefault("USERS_TABLE", "boardsite-users-dev")

    from lib.db.users import list_users  # deferred: --env must set USERS_TABLE first

    items = list_users()
    if not items:
        print("No users found.")
        return
    items.sort(key=lambda u: u.get("createdAt", ""))
    print(f"{'Username':<20} {'Display Name':<25} {'Role':<10} {'Created'}")
    print("-" * 75)
    for u in items:
        created = u.get("createdAt", "")[:10]
        # `pk` is the username. Only scripts/create-user.py also writes a
        # separate `username` attribute; users created through the web UI
        # (POST /api/users) have `pk` alone, and reading `username` here used
        # to raise KeyError for them. GET /api/users already reads `pk`.
        username = u.get("username") or u["pk"]
        print(f"{username:<20} {u.get('displayName', ''):<25} {u.get('role', ''):<10} {created}")


if __name__ == "__main__":
    main()
