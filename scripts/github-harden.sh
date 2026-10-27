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

# Rebase-only: a merge commit repeats the PR title in its body and
# release-please lists the change twice; a squash collapses several
# feat/fix commits into one changelog line. Merged branches are deleted.
echo "→ merge settings (rebase only, delete merged branches)"
gh api -X PATCH "repos/$REPO" \
  -F allow_merge_commit=false \
  -F allow_squash_merge=false \
  -F allow_rebase_merge=true \
  -F delete_branch_on_merge=true \
  --jq '{allow_merge_commit, allow_squash_merge, allow_rebase_merge, delete_branch_on_merge}'

echo "→ branch protection on main (CI required, linear history, no force-push, no deletion)"
gh api -X PUT "repos/$REPO/branches/main/protection" --input - <<'JSON'
{
  "required_status_checks": {
    "strict": false,
    "contexts": ["API tests", "TypeScript typecheck", "Frontend tests", "Lint", "Docker build", "Commit messages"]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": null,
  "restrictions": null,
  "required_linear_history": true,
  "allow_force_pushes": false,
  "allow_deletions": false
}
JSON

echo "✓ done"
