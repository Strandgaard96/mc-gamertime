---
title: AWS Deploy
description: Deploy MC GamerTime to AWS
sidebar:
  order: 1
---

An optional path — for public access without running your own reverse proxy, AWS's built-in security, or simply to learn AWS hosting. Costs roughly $0/month for personal use.

## Prerequisites

- **A domain name you own.** There is no way around this: CloudFront needs an ACM
  certificate, and ACM only issues one for a domain you can prove you control. Register one
  at any registrar — DNS records are added by hand (see below), so any provider works.
- An AWS account
- [AWS CLI](https://aws.amazon.com/cli/) configured with credentials
- [Terraform](https://developer.hashicorp.com/terraform/install) >= 1.5
- [Node.js](https://nodejs.org) >= 20
- [uv](https://docs.astral.sh/uv/) (packages the Lambda and runs the user scripts)
- [Task](https://taskfile.dev/installation/) (task runner)

You will add two DNS records by hand during setup: one to validate the certificate, one to
point your subdomain at CloudFront. Both are plain CNAMEs.

:::caution
Misconfiguring an AWS environment can lead to SEVERE billing consequences. This project's services are pay-per-request by design, but accidentally configuring the backend Lambda to always be running (e.g. provisioned concurrency) can lead to a SIGNIFICANT bill. Take caution.
:::

## Configure your deployment

Terraform reads deployment-specific values from `infra/terraform.tfvars`, which is
gitignored so nobody's domain or AWS account id ends up in version control. Do this before
the first `task apply`:

```sh
cp infra/terraform.tfvars.example infra/terraform.tfvars
```

**`domain` is the only required variable.** A file containing just `domain = "example.com"`
is enough for a first deploy; there is no separate Lambda environment setup — `infra/lambda.tf`
derives everything from these variables.

### Worth setting before the first apply

| Variable | Default | Why now rather than later |
|---|---|---|
| `subdomain` | `mcgamertime` | Gives `mcgamertime.example.com`. Changing it later means a new certificate and a new DNS record |
| `bgg_token` | empty | Enables Board Game Geek search ([apply for a token](https://boardgamegeek.com/using_the_xml_api)). Stored in SSM with `lifecycle.ignore_changes`, so it is read **only on the first apply**; adding it afterwards means editing the SSM parameter by hand |
| `aws_region` | `eu-west-1` | Where Lambda, DynamoDB and S3 land. Moving region later means recreating everything, data included |

### Optional, changeable any time

| Variable | Default | What it does |
|---|---|---|
| `alert_email` | empty | Subscribes an address to the CloudWatch alarm topic (Lambda errors, throttles, API Gateway 5xx). AWS emails a confirmation link once — until you click it, alarms fire into a topic nobody reads |
| `cloudfront_web_acl_arn` | empty | ARN of a CloudFront-scoped WAF Web ACL. Empty deploys without a WAF |
| `extra_cors_origins` | `[]` | Extra credentialed CORS origins beyond the deployed FQDN. The FQDN and the distribution's own `*.cloudfront.net` name are always included |

:::tip[Free WAF: enable Core protections]
Leaving `cloudfront_web_acl_arn` empty on the prod (`default`) workspace prints a
non-blocking warning on every `plan`/`apply` — the app's own auth, rate limiting and CSRF
checks hold with no WAF at all, so this is a nudge, not a gate.

To close it at no extra cost: after your first `task apply`, open the CloudFront console →
your distribution → **Security** tab → **Enable protections** → **Core protections**. Do
**not** pick Additional protections (Bot Control, Account Takeover Prevention, etc.) — those
bill separately. Copy the Web ACL ARN it creates into `cloudfront_web_acl_arn` in
`terraform.tfvars`, then `task apply` again.
:::

:::caution
Once you have set `cloudfront_web_acl_arn`, do not apply with it emptied — that
disassociates the WAF from the live distribution. The ARN embeds your AWS account id, which
is one reason this file stays gitignored. Keep a copy of `terraform.tfvars` somewhere
outside the repo; losing it breaks your next apply.
:::

## Deploy

### 1. Provision the infrastructure

```sh
task init    # terraform init + npm ci
task build   # bundle Lambda + build Vite SPA
task plan    # review what Terraform will create
task apply   # provision infrastructure
```

The first apply stops at the ACM certificate, which stays `PENDING_VALIDATION` until you
prove you own the domain — the next step.

### 2. Validate the certificate (one-time)

Get the records ACM wants:

```sh
terraform -chdir=infra output acm_validation_records
```

Add each one as a **CNAME** at whatever DNS provider hosts your domain, using the output's
`name` field as the record name and `value` as the target. Wait ~2 minutes for it to
propagate, then run `task apply` again — this time it completes.

### 3. Point your subdomain at CloudFront

```sh
terraform -chdir=infra output cloudfront_url
```

Add a second CNAME: your `subdomain` (default `mcgamertime`) → the `*.cloudfront.net` value
from that output.

:::note[Using Cloudflare?]
Both records must be **DNS only** (proxied = off, grey cloud). CloudFront rejects requests
carrying Cloudflare's proxy headers, so an orange-cloud record breaks the site rather than
protecting it. Security is handled at the AWS level.
:::

### 4. Ship the frontend

Once the subdomain resolves to CloudFront:

```sh
task deploy   # run this every time you want to update your live application
```

### 5. Create the first admin user

Nothing on the cloud path creates an account for you — `ADMIN_USERNAME`/`ADMIN_PASSWORD`
bootstrap only applies to the self-hosted container. Until you run this, the login page
loads and no password works:

```sh
task create-user -- --username admin --display-name "Admin" --role admin --password <your-password>
```

The task writes straight to DynamoDB with your local AWS credentials, so run it from a
clone of the repo, after `task apply` has created the tables. If your `aws_region` is not
the AWS CLI's configured default, prefix it: `AWS_REGION=<your-region> task create-user -- ...`.

Then open `https://<subdomain>.<your-domain>` and log in.

:::danger
`task destroy` tears down all AWS infrastructure including DynamoDB tables. All data will be lost.
:::

## Security and privacy

Uploaded media requires a session, the bucket is not public, and nothing leaves your AWS
account. [Security & Privacy on AWS](/cloud-deploy/security/) documents what is enforced,
what is deliberately public, and what you remain responsible for — with commands to verify
each claim yourself.

## Architecture

```
Browser → CloudFront → API Gateway → Lambda → DynamoDB + S3
```

- **Frontend:** Vite SPA served from S3 via CloudFront
- **Backend:** FastAPI on Lambda via Mangum + API Gateway HTTP API
- **Database:** DynamoDB (pay-per-request, free tier covers personal use)
- **Storage:** S3 (avatars, blog images — free tier covers personal use)
- **DNS:** a CNAME at your own DNS provider → CloudFront distribution (no Route 53)
- **TLS:** ACM certificate (us-east-1, CloudFront requirement)
