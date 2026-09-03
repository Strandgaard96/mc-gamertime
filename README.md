# MC GamerTime

[![CI](https://github.com/Strandgaard96/mc-gamertime/actions/workflows/ci.yml/badge.svg)](https://github.com/Strandgaard96/mc-gamertime/actions/workflows/ci.yml)
[![Docker image](https://img.shields.io/badge/ghcr.io-strandgaard96%2Fmc--gamertime-2496ED?logo=docker&logoColor=white)](https://github.com/Strandgaard96/mc-gamertime/pkgs/container/mc-gamertime)
[![Release](https://img.shields.io/github/v/release/Strandgaard96/mc-gamertime)](https://github.com/Strandgaard96/mc-gamertime/releases)
[![License: MIT](https://img.shields.io/github/license/Strandgaard96/mc-gamertime)](LICENSE)
[![Docs](https://img.shields.io/badge/docs-mcgamertime--docs.drmaggi.com-blue)](https://mcgamertime-docs.drmaggi.com)
[![Built with Claude Code](https://img.shields.io/badge/built%20with-Claude%20Code-8A2BE2)](#built-with-claude-code)

**Board game inventory tracker and game logger: Elo ratings, head-to-head records, achievements, per-player stats, a Board Game
Geek integration for the catalog.**

Self-host it, or use the built-in support for serverless hosting on AWS for ≈$0 a month.

![The leaderboard: podium, Elo ratings per player, win rates and streaks](docs-site/src/assets/hero-leaderboard.png)

| | |
|---|---|
| ![Game catalog: Board Game Geek metadata, play counts and cover art](docs-site/src/assets/screenshot-catalog.webp) | ![Player profile: win rate, streaks, favourite game and nemesis](docs-site/src/assets/screenshot-player.png) |



## Contents

- [Built with Claude Code](#built-with-claude-code)
- [Quick start](#quick-start)
  - [1. Self-hosted with Docker](#1-self-hosted-with-docker)
  - [2. Cloud-hosted on AWS](#2-cloud-hosted-on-aws)
- [Stack](#stack)
- [Features](#features)
- [Contributing](#contributing)
- [License](#license)

## Built with Claude Code

Claude Code wrote most of the code. My background is scientific computing with extensive
AWS experience and I did this project to learn frontend coding and agent orchestration in a full-stack application.

The setup used to build it is in [CLAUDE.md](./CLAUDE.md), with these plugins:

- [superpowers](https://github.com/obra/superpowers) — brainstorming, subagent-driven development, TDD, systematic debugging
- [frontend-design](https://github.com/anthropics/claude-plugins-public/tree/main/plugins/frontend-design) — non-generic UI design guidance
- [chrome-devtools-mcp](https://github.com/ChromeDevTools/chrome-devtools-mcp) — live browser inspection and automation

## Quick start

### 1. Self-hosted with Docker

One container, embedded SQLite, local file storage.

Claude wrote most of the code and one should therefore take care and treat it like any other open source project.

**To install:**

```bash
curl -fsSL https://raw.githubusercontent.com/Strandgaard96/mc-gamertime/main/docker-compose.yml -o docker-compose.yml
echo "ADMIN_USERNAME=admin" >> .env
echo "ADMIN_PASSWORD=<your-password>" >> .env
docker compose up -d
```

Open <http://localhost:4263> and log in.

Going beyond your own machine? Put TLS in front of it — Tailscale is the least work, a
reverse proxy is the alternative. See [HTTPS / Reverse
Proxy](https://mcgamertime-docs.drmaggi.com/self-hosting/https/) and the
[security model](https://mcgamertime-docs.drmaggi.com/self-hosting/security/).

[Full self-hosting guide →](https://mcgamertime-docs.drmaggi.com/self-hosting/quickstart/)

### 2. Cloud-hosted on AWS

The same app, hosted on AWS serverless infrastructure and provisioned by Terraform. Everything
is pay-per-request, which for regular personal use amounts to roughly **$0/month** — the free tier covers
it. Worth choosing if you want easy remote access and experience with cloud hosting while gaining the security benefits of AWS hosted infrastructure.

#### Prerequisites
An AWS account, plus Terraform, Node.js and Task installed — and **a domain name you own**.
The domain is not optional: CloudFront needs an ACM certificate, and ACM only issues one for
a domain you control. Any registrar works; Route 53 is not required, since you add the DNS
records by hand. Set `domain` in `infra/terraform.tfvars` before the first apply — it is the
only variable with no default, and Terraform refuses to run without it.

For full installation instructions see: [Full AWS guide →](https://mcgamertime-docs.drmaggi.com/cloud-deploy/aws/).

The security considerations for the AWS hosted app are described here:
[Security & privacy on AWS →](https://mcgamertime-docs.drmaggi.com/cloud-deploy/security/).


## Stack

- **Frontend** — React 18, Vite, TypeScript, Tailwind, TanStack Query, Recharts
- **Backend** — Python, FastAPI; uvicorn when self-hosted, Lambda + Mangum on AWS
- **Data** — embedded SQLite, or DynamoDB
- **Storage** — local filesystem, or S3; uploaded media is served by the app behind auth,
  never straight from the bucket
- **Infra** — Terraform, GitHub Actions, release-please

![Architecture: the same FastAPI app and React build served either from one self-hosted container backed by SQLite and the local filesystem, or on AWS behind CloudFront with API Gateway, Lambda, DynamoDB and S3](docs-site/src/assets/architecture.svg)

<details>
<summary>Diagram source (Mermaid)</summary>

```mermaid
graph LR
  B["Browser"]
  B -->|"self-hosted"| C["one container<br/>FastAPI, serving the React build"]
  C --> SQ[("SQLite file")]
  C --> FS[("local filesystem")]
  B -->|"AWS"| CF["CloudFront"]
  CF --> S3[("S3<br/>static bundle")]
  CF --> AG["API Gateway"]
  AG --> L["Lambda<br/>the same FastAPI app"]
  L --> DDB[("DynamoDB")]
  L --> S3M[("S3<br/>uploaded media")]
```

</details>

## Features

| | |
|---|---|
| **Leaderboard** | Elo rating per player, win rates, streaks, head-to-head records |
| **Game catalog** | Search Board Game Geek, keep player counts, weights and cover art |
| **Session log** | Who played, who won, seats, scores, mood — plus per-game custom fields |
| **Achievements** | Milestones detected automatically as results come in |
| **Player profiles** | Favourite game, nemesis, best month, Elo history |
| **Blog** | Session recaps with rich text and images |

[Screenshots and detail →](https://mcgamertime-docs.drmaggi.com/self-hosting/features/)


## Contributing

- [Contributing guide](./CONTRIBUTING.md)
- [Architecture walkthrough](https://mcgamertime-docs.drmaggi.com/contributing/architecture/) — how a request flows end to end
- [Recipes](https://mcgamertime-docs.drmaggi.com/contributing/recipes/) — add an endpoint, a page, a table
- [Security policy](./SECURITY.md) — report a vulnerability privately

## License

[MIT](./LICENSE)
