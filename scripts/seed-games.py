#!/usr/bin/env python3
"""
Seed the game catalog with popular board games using canonical BGG IDs.
Usage: python3 scripts/seed-games.py --username admin --password <pw>
       API_URL=https://your-app.example.com/api python3 scripts/seed-games.py --username admin --password <pw>

Defaults to the local dev API; set API_URL to target a deployed instance.
"""

import argparse
import os
import sys
import httpx

API_URL = os.environ.get("API_URL", "http://localhost:8000/api")

# Canonical BGG IDs for popular games
GAMES_TO_SEED = [
    13,  # Catan
    9209,  # Ticket to Ride
    30549,  # Pandemic
    822,  # Carcassonne
    230802,  # Azul
    266192,  # Wingspan
    36218,  # Dominion
    167791,  # Terraforming Mars
    68448,  # 7 Wonders
    178900,  # Codenames
]


def seed(username: str, password: str) -> None:
    with httpx.Client(base_url=API_URL, timeout=30.0) as client:
        # Login
        resp = client.post(
            "/auth/login", json={"username": username, "password": password}
        )
        if resp.status_code != 200:
            print(f"Login failed: {resp.status_code} {resp.text}")
            sys.exit(1)
        token = resp.cookies.get("token")
        if not token:
            print("No token cookie in login response")
            sys.exit(1)
        client.cookies.set("token", token)
        print(f"Logged in as {username}\n")

        for bgg_id in GAMES_TO_SEED:
            try:
                # Fetch full detail from BGG
                r = client.get("/games/search", params={"bggId": bgg_id})
                r.raise_for_status()
                detail = r.json()

                # Save to catalog
                r = client.post("/games", json={**detail, "tags": []})
                r.raise_for_status()
                print(f"  ✓ Added \"{detail['name']}\" (BGG {detail['bggId']})")

            except Exception as e:
                print(f"  ✗ Error for BGG {bgg_id}: {e}")

    print("\nDone.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()
    seed(args.username, args.password)
