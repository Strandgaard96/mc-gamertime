#!/usr/bin/env python3
"""Create a boardsite user.

cd api && uv run python3 scripts/create-user.py --username alice --display-name "Alice" --role readonly --password secret [--env dev]
"""

import argparse
import getpass
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import bcrypt  # noqa: E402


def _prompt_for_args() -> argparse.Namespace:
    print("No arguments given — interactive setup.\n")
    username = input("Username: ").strip()
    while not username:
        username = input("Username (required): ").strip()

    display_name = input("Display name: ").strip()
    while not display_name:
        display_name = input("Display name (required): ").strip()

    role = ""
    while role not in ("admin", "readonly"):
        role = input("Role [admin/readonly] (default: admin): ").strip().lower() or "admin"

    password = getpass.getpass("Password: ")
    confirm = getpass.getpass("Confirm password: ")
    while not password or password != confirm:
        if password != confirm:
            print("Passwords did not match — try again.")
        password = getpass.getpass("Password: ")
        confirm = getpass.getpass("Confirm password: ")

    return argparse.Namespace(
        username=username,
        display_name=display_name,
        role=role,
        password=password,
        email=None,
        env="prod",
    )


def main():
    parser = argparse.ArgumentParser(description="Create a boardsite user")
    parser.add_argument("--username")
    parser.add_argument("--display-name")
    parser.add_argument("--role", choices=["admin", "readonly"])
    parser.add_argument("--password")
    parser.add_argument("--email", help="Optional — required for self-service password reset")
    parser.add_argument("--env", choices=["prod", "dev"], default="prod")

    if len(sys.argv) == 1 and sys.stdin.isatty():
        args = _prompt_for_args()
    else:
        args = parser.parse_args()
        missing = [
            flag
            for flag, value in (
                ("--username", args.username),
                ("--display-name", args.display_name),
                ("--role", args.role),
                ("--password", args.password),
            )
            if not value
        ]
        if missing:
            parser.error(f"the following arguments are required: {', '.join(missing)}")

    if args.env == "dev":
        os.environ.setdefault("USERS_TABLE", "boardsite-users-dev")

    from lib.db.users import get_user, put_user  # deferred: --env must set USERS_TABLE first

    if get_user(args.username):
        print(f"User '{args.username}' already exists.")
        sys.exit(1)

    hashed = bcrypt.hashpw(args.password.encode(), bcrypt.gensalt()).decode()
    now = datetime.now(timezone.utc).isoformat()
    item = {
        "pk": args.username,
        "createdAt": now,
        "username": args.username,
        "displayName": args.display_name,
        "role": args.role,
        "passwordHash": hashed,
    }
    if args.email:
        item["email"] = args.email
    put_user(item)
    print(f'Created: {args.username} ({args.role}) — "{args.display_name}"')


if __name__ == "__main__":
    main()
