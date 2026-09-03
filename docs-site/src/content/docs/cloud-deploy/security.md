---
title: Security & Privacy on AWS
description: What the AWS deployment exposes, what it keeps private, and what you are responsible for.
sidebar:
  order: 2
---

The short version: **nothing you upload is world-readable, and nothing leaves your AWS
account.** This page says exactly how that is enforced, so you can check the claims rather
than take them on faith.

## Where your data lives

Everything stays inside your own AWS account, in the region you deploy to (`eu-west-1` by
default):

| Data | Where | Notes |
|---|---|---|
| Games, results, posts, users | DynamoDB, one table per type | Point-in-time recovery enabled, 35-day window |
| Avatars and uploaded images | S3, one bucket | Served only through the app — see below |
| Secrets (JWT signing key, tokens) | SSM Parameter Store, `SecureString` | Encrypted at rest, fetched at cold start |
| Logs | CloudWatch, 30-day retention | Request metadata, no passwords or tokens |

There is no third-party analytics, no error-reporting service, no CDN other than
CloudFront, and no outbound call except to Board Game Geek when you search for a game.

## Nothing in the bucket is public

The S3 bucket has all four [public access block](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html)
settings on, and its policy grants read access to exactly one principal — the CloudFront
service — restricted to your distribution's ARN. Requests straight to the bucket URL
return `403` even for a file that renders fine in the app.

**Uploaded media requires a session.** Avatars and images are *not* served from S3 by the
CDN. CloudFront routes `/avatars/*`, `/blog-images/*` and `/game-images/*` to the API,
which checks your session cookie before streaming the bytes. Fetch one without logging in
and you get `401`, not the image.

That matters more than it sounds: avatar keys are just the username, so if they were served
publicly, anyone could guess `/avatars/<name>.png` for any member. The bucket policy also
carries an explicit `Deny` on those prefixes plus `exports/`, so a future misconfiguration
cannot quietly republish them.

:::note
`exports/` is where `scripts/export-tables.py` writes table dumps if you use it. Those
contain everything, including password hashes. The `Deny` above means CloudFront will not
serve them under any circumstances — but treat the dumps themselves like a database backup,
because that is what they are.
:::

## Caching

Two rules, both aimed at stopping a copy of your data resting somewhere it shouldn't:

- **API responses** (`/api/*`) are sent `Cache-Control: no-store`. No proxy, CDN or browser
  history cache retains them, which is also what makes the back button after logout show
  nothing.
- **Uploaded media** is sent `Cache-Control: private, max-age=1200`. `private` keeps it out
  of CloudFront and every other shared cache; the 20 minutes applies only to the browser
  that authenticated for it, so a page of avatars isn't refetched on every navigation.
  Avatar URLs carry a `?v=` stamp, so replacing a picture takes effect immediately.

## In transit

CloudFront serves HTTPS only and redirects HTTP. Every response carries HSTS
(`max-age=63072000; includeSubDomains`), `X-Content-Type-Options: nosniff`,
`X-Frame-Options: DENY`, a Content-Security-Policy limiting scripts to same-origin, and
`Referrer-Policy: strict-origin-when-cross-origin`. The TLS certificate is issued by ACM
and renews automatically.

The API is not reachable directly. API Gateway sits behind CloudFront, and the app rejects
any request that doesn't carry the shared origin token CloudFront injects — so bypassing
the CDN to hit the origin returns `403`.

## Accounts and access

- **No public signup.** Accounts exist only if an admin creates them, so an
  internet-facing instance isn't an open door or a spam target.
- **Passwords** are bcrypt cost-12 hashed, minimum 12 characters, never logged or returned.
- **Sessions** are JWTs in an `HttpOnly`, `Secure`, `SameSite=Strict` cookie. Every request
  re-checks the user's `tokenVersion`, so logging out or running
  `scripts/revoke-sessions.py` invalidates every session for that user immediately —
  including any image it could load.
- **Failed logins** apply per-account exponential backoff on top of a 5-per-minute IP rate
  limit, and are recorded to a security log.
- **Admin actions** re-read the role from the database rather than trusting the token, so a
  demoted admin loses access at once.

## What is deliberately public

Only two things, and only if you leave them on:

- The landing page and the **recommended games** list, when
  `PUBLIC_RECOMMENDED_ENABLED=true` (the default for the cloud deployment). Cover art on
  that page comes from Board Game Geek's own CDN, not your bucket. Set it to `false` if you
  want nothing at all visible without a login.
- The static frontend bundle — HTML, JS, CSS, icons. It contains no data.

Everything else, including every result, player, post and image, requires a session.

## What is on you

The deployment is only as private as the account it runs in:

- **Protect the AWS account itself.** MFA on the root user, no long-lived access keys
  lying around. Anyone with account access can read DynamoDB and S3 directly, whatever the
  app enforces.
- **Set `alert_email`** in `terraform.tfvars` and confirm the SNS subscription, or the
  CloudWatch alarms fire into a topic nobody receives.
- **Guard `infra/terraform.tfvars` and any table dumps.** They are gitignored for a
  reason.
- **Rotate the JWT secret** if you suspect it leaked; every session dies with it.

## Verifying it yourself

None of this requires trust:

```bash
# Uploaded media rejects anonymous access
curl -o /dev/null -w '%{http_code}\n' https://your-domain/avatars/<someone>.png     # 401

# The bucket refuses direct reads
curl -o /dev/null -w '%{http_code}\n' https://<bucket>.s3.<region>.amazonaws.com/avatars/<someone>.png   # 403

# API responses are not cacheable
curl -sD - -o /dev/null https://your-domain/api/recommended | grep -i cache-control  # no-store

# The origin is not reachable without CloudFront's token
curl -o /dev/null -w '%{http_code}\n' https://<api-id>.execute-api.<region>.amazonaws.com/api/health   # 403
```
