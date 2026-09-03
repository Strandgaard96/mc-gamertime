#!/usr/bin/env bash
# Enable GitHub's free public-repo protections. Both features are gated behind
# GitHub Pro / public visibility, so this can only run AFTER the repo is public.
#
#   ./scripts/github-harden.sh Strandgaard96/mc-gamertime
set -euo pipefail

REPO="${1:?usage: github-harden.sh <owner>/<repo>}"

echo "→ secret scanning + push protection"
gh api -X PATCH "repos/$REPO" \
  -f 'security_and_analysis[secret_scanning][status]=enabled' \
  -f 'security_and_analysis[secret_scanning_push_protection][status]=enabled' \
  --jq '.security_and_analysis'

echo "→ branch protection on main (CI required, no force-push, no deletion)"
gh api -X PUT "repos/$REPO/branches/main/protection" --input - <<'JSON'
{
  "required_status_checks": {
    "strict": false,
    "contexts": ["API tests", "TypeScript typecheck", "Frontend tests", "Lint", "Docker build"]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": null,
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
JSON

echo "✓ done"
