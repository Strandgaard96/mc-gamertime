#!/usr/bin/env python3
"""Delete a boardsite user.

cd api && uv run python3 scripts/delete-user.py --username alice [--env dev]
"""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def main():
    parser = argparse.ArgumentParser(description="Delete a boardsite user")
    parser.add_argument("--username", required=True)
    parser.add_argument("--yes", action="store_true", help="skip confirmation prompt")
    parser.add_argument("--env", choices=["prod", "dev"], default="prod")
    args = parser.parse_args()

    if args.env == "dev":
        os.environ.setdefault("USERS_TABLE", "boardsite-users-dev")

    from lib.db.users import delete_user, get_user  # deferred: --env must set USERS_TABLE first

    user = get_user(args.username)
    if not user:
        print(f"User '{args.username}' not found.")
        sys.exit(1)

    if not args.yes:
        confirm = input(
            f"Delete '{args.username}' ({user['role']}) — \"{user['displayName']}\"? [y/N] "
        )
        if confirm.lower() != "y":
            print("Aborted.")
            sys.exit(0)

    delete_user(args.username)
    print(f"Deleted: {args.username}")


if __name__ == "__main__":
    main()
