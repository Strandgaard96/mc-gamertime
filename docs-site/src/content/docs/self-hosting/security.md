---
title: Security Model
description: What the self-hosted stack exposes, what it assumes about your network, and what to change before putting it on the internet.
sidebar:
  order: 4
---

The defaults assume the app runs on a network you trust — your LAN, or a Tailscale
network. They do not assume the open internet. This page says exactly what that means, so
you can decide what to change before exposing it more widely.

## What is exposed

The stack publishes **one** port: `4263`, the same on the host and in the container,
bound to `127.0.0.1` by default so only this host (and a reverse proxy running on it) can
reach it. Set `APP_BIND=0.0.0.0` to expose it to the LAN directly — see
[Configuration](/self-hosting/configuration/#host-port-and-bind-address); Docker port
bindings bypass `ufw`/`firewalld`, so that setting is the only firewall the app has.
Everything is behind it: the API, the React app, and the authenticated `/storage` proxy
that serves avatars and uploaded images.

Every route requires a logged-in session except these:

| Route | Why it is open |
|---|---|
| `GET /api/health` | Liveness check for the container healthcheck |
| `POST /api/auth/login` | You need to be able to log in |
| `POST /api/auth/forgot-password`, `POST /api/auth/reset-password` | Self-service password reset, if enabled |
| `GET /metrics` | Only when you set `METRICS_ENABLED=true` — see below |

There is **no public signup**. Accounts exist only if an admin creates them, so an
internet-exposed instance is not a spam target the way an open-registration app is.

## Optional public surface

One more thing becomes public, but only if you turn it on: setting
`PUBLIC_RECOMMENDED_ENABLED=true` (default `false` for self-hosted — see [App service
variables](/self-hosting/configuration/#app-service-variables)) exposes the landing page's
recommended-games list, `GET /api/recommended*`, without a session — the same behavior the
AWS deployment defaults to. Leave it `false` if you want nothing at all visible without
logging in.

## What the defaults assume

:::caution
Three defaults are chosen for a trusted network. Change them before exposing the app
beyond your LAN.
:::

**No TLS.** The container serves plain HTTP. Passwords and session cookies cross the
network unencrypted unless you put a TLS-terminating proxy in front — see
[HTTPS / Reverse Proxy](/self-hosting/https/). This is the one that matters most.

**`ORIGIN_GUARD_ENABLED=false`.** The origin guard is a shared-secret header check that
only makes sense behind CloudFront, where the CDN injects the header and the origin
rejects anything else. Self-hosted, there is no CDN to inject it, so it is off. Your
reverse proxy is the access-control boundary instead.

**`METRICS_ENABLED` is off, and unauthenticated when on.** `/metrics` sits behind no auth
of its own. Enabling it while the app is publicly reachable publishes your request counts,
latencies, and route names to anyone who asks. Scrape it from inside your Docker network,
never through the public proxy.

## Passwords and sessions

Passwords are hashed with **bcrypt at cost 12** and are never logged or returned by the
API. A minimum length of 12 characters is enforced server-side — by the API itself, not
just the browser, so it holds for direct `curl` calls too. There are no composition rules
(no forced symbol or digit), following current NIST guidance: length does the real work,
while composition rules mostly push people toward predictable patterns.

Sessions are **JWTs in an HttpOnly, SameSite=Strict cookie**, valid for 7 days. HttpOnly
keeps JavaScript from reading the token, and SameSite=Strict is what defends against CSRF.
There is no idle timeout: a session lives its full 7 days unless invalidated.

Each user has a `tokenVersion`. Bumping it invalidates every existing session for that
user immediately:

```bash
docker compose exec mc-gamertime python3 scripts/revoke-sessions.py --username alice
```

Changing a password bumps it too, so a password reset signs out every other device.

:::note
The `Secure` flag on that cookie follows the transport: present over HTTPS, omitted over
plain HTTP. Browsers refuse to store a `Secure` cookie from an insecure origin, so setting
it unconditionally would break login on a LAN address instead of protecting anything — the
value has already travelled in the clear at that point. Put TLS in front (see
[HTTPS / Reverse Proxy](/self-hosting/https/)) and the flag comes back automatically,
including when the proxy speaks plain HTTP to the container.
:::

## The JWT secret

Generated on first boot, stored at `/data/.jwt_secret` (mode `0600`) inside the
bind-mounted `config/app/` directory. It is never written to `.env`, never logged, and
never served over HTTP — `/data` is outside both `STATIC_DIR` and the `/storage` proxy's
allowed prefixes.

Anyone holding it can mint a valid session for any user, so treat it like a password: it
is the most sensitive thing in your backups. To rotate it — after a lost backup or a
compromised host — see [Rotating the JWT secret](/self-hosting/configuration/#rotating-the-jwt-secret).
Every session everywhere is invalidated.

## Rate limiting

Login and password-reset accept **5 requests per minute per IP**. Behind a reverse proxy
this only works if the app can see the real client IP; `FORWARDED_ALLOW_IPS` already
trusts private and Docker-internal ranges, which covers every proxy setup in the HTTPS
guide. Get this wrong and every visitor shares one bucket — see
[Reverse proxy and rate limiting](/self-hosting/configuration/#reverse-proxy-and-rate-limiting).

## Uploads

Uploaded images are constrained on the way in and on the way out:

- The stored file extension comes from the **allowlisted content type**, never from the
  filename a client sends, so an `evil.svg` uploaded as `image/png` is stored as `.png`
- The `/storage` proxy serves only the `avatars/`, `blog-images/`, and `game-images/`
  prefixes; nothing else under `/data` is reachable through it
- Blog HTML is sanitised with DOMPurify before rendering

## Response headers

Every response carries `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`
(clickjacking), `Referrer-Policy: strict-origin-when-cross-origin`, HSTS, and a
Content-Security-Policy restricting scripts to same-origin.

## Reporting a vulnerability

Please **do not** open a public issue. Use GitHub's **Security → Report a vulnerability**
on the [repository](https://github.com/Strandgaard96/mc-gamertime/security), which opens a
private advisory. This is a hobby project with no formal SLA, but reports get read.
