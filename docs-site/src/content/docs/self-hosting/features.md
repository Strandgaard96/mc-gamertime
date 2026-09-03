---
title: Features
description: What MC GamerTime includes — leaderboard, game catalog, achievements, and more.
sidebar:
  order: 2
---

MC GamerTime is a full-stack web app for tracking board game nights with friends. It can be either self-hosted or deployed to AWS for near 0 cost. Here's what you get out of the box.

## Leaderboard

![The leaderboard: podium, Elo ratings, win rates and streaks](../../../assets/hero-leaderboard.png)

Track wins, losses, and an Elo rating for every player across all games. Sortable by rating, win rate, and total games played. Includes head-to-head records between players.

## Game Catalog

![The game catalog, showing cover art, player counts and play counts](../../../assets/screenshot-catalog.webp)

Search the Board Game Geek database to add games to your library. Each game stores player count, complexity rating, and full BGG metadata including cover art. Requires a BGG API token — see [Configuration](/self-hosting/configuration/).

## Log a Result

![The chronicle of logged sessions, grouped by month](../../../assets/screenshot-log.png)

Record who played, who won, seat positions, player scores, and session mood. Supports per-game custom variables (e.g. faction played, score breakdown, role). Editing a past result is supported.

## Achievements

Automatic milestone detection on every result submission — first win, 10th game played, winning streak, and more. Players see earned achievements on their profile. New achievement definitions are added in code.

## Records

![A player profile: games played, win rate, streaks, favourite game and nemesis](../../../assets/screenshot-player.png)

Per-player and per-game statistics: win rates, most-played games, longest streaks, best month, Elo history chart. Also shows leaderboard podium animations and head-to-head tables.

## Blog

Write session recaps with rich text and embedded images. Images are uploaded to local filesystem storage and served via the app proxy — no external image hosting needed.

## User management

Admins manage users from the app itself — create, edit, and delete accounts on the Users
page. The same operations exist as CLI scripts (`scripts/create-user.py`,
`update-user.py`, `delete-user.py`, `revoke-sessions.py`), which is how you bootstrap the
very first admin and how you revoke every session for a user.

Two roles: `admin` (full CRUD) and `readonly` (no admin actions, but can still react,
comment, favorite games, and set their own avatar).
