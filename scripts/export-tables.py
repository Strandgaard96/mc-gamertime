#!/usr/bin/env python3
"""Export all boardsite DynamoDB tables to JSON files.

Usage (boto3 comes from the api venv):
  cd api && uv run python3 ../scripts/export-tables.py            # prod tables -> ../exports/YYYY-MM-DD/
  cd api && uv run python3 ../scripts/export-tables.py --env dev  # dev tables
  cd api && uv run python3 ../scripts/export-tables.py --s3 <a-private-backup-bucket>

The dumps contain every table, including users with their bcrypt password hashes.
Treat them like a database backup. Do NOT upload them to the bucket that serves the
website: CloudFront serves that bucket at the site root, and only an explicit Deny in
infra/s3.tf on the exports/ prefix stops them being published.
"""
import argparse
import json
from datetime import date
from decimal import Decimal
from pathlib import Path

import boto3

TABLES = ["users", "games", "results", "posts", "recs", "reactions", "notifications", "settings"]


def _json_default(obj):
    if isinstance(obj, Decimal):
        return int(obj) if obj == obj.to_integral_value() else float(obj)
    raise TypeError(f"Not JSON serializable: {type(obj)}")


def paginated_scan(table) -> list[dict]:
    items: list[dict] = []
    kwargs: dict = {}
    while True:
        resp = table.scan(**kwargs)
        items.extend(resp.get("Items", []))
        last = resp.get("LastEvaluatedKey")
        if not last:
            break
        kwargs["ExclusiveStartKey"] = last
    return items


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env", choices=["prod", "dev"], default="prod")
    parser.add_argument("--region", default="eu-west-1")
    parser.add_argument("--s3", metavar="BUCKET", help="also upload to s3://BUCKET/exports/YYYY-MM-DD/")
    parser.add_argument("--out", default=None, help="output dir (default: <repo>/exports/YYYY-MM-DD)")
    args = parser.parse_args()

    suffix = "-dev" if args.env == "dev" else ""
    stamp = date.today().isoformat()
    out_dir = Path(args.out) if args.out else Path(__file__).resolve().parent.parent / "exports" / stamp
    out_dir.mkdir(parents=True, exist_ok=True)

    dynamo = boto3.resource("dynamodb", region_name=args.region)
    s3 = boto3.client("s3", region_name=args.region) if args.s3 else None

    for short in TABLES:
        table_name = f"boardsite-{short}{suffix}"
        table = dynamo.Table(table_name)
        items = paginated_scan(table)
        path = out_dir / f"{table_name}.json"
        path.write_text(json.dumps(items, default=_json_default, indent=2))
        print(f"{table_name}: {len(items)} items -> {path}")
        if s3:
            key = f"exports/{stamp}/{table_name}.json"
            s3.upload_file(str(path), args.s3, key)
            print(f"  uploaded s3://{args.s3}/{key}")


if __name__ == "__main__":
    main()
