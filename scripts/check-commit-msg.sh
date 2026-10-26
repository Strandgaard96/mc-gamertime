#!/usr/bin/env bash
# Conventional Commits gate, shared by the commit-msg prek hook and CI's
# "Commit messages" job. PRs are rebase-merged, so every commit lands on main
# as written and release-please reads its subject: one that doesn't match is
# silently left out of the changelog.
#
#   scripts/check-commit-msg.sh <file>   hook: first line of a commit message file
#   scripts/check-commit-msg.sh          CI: one subject per line on stdin
set -euo pipefail

pattern='^(feat|fix|perf|refactor|docs|test|build|ci|chore|style|revert)(\([^()]+\))?!?: [^ ]'

if [ $# -gt 0 ]; then
  subject=$(head -n 1 "$1")
  # git creates these itself; fixups are squashed away before the PR merges,
  # and CI checks with --no-merges.
  case "$subject" in
    "Merge "* | "fixup! "* | "squash! "* | "amend! "*) exit 0 ;;
  esac
  subjects=$subject
else
  subjects=$(cat)
fi

bad=0
while IFS= read -r s; do
  [ -z "$s" ] && continue
  if ! [[ $s =~ $pattern ]]; then
    echo "not a Conventional Commit: $s" >&2
    bad=1
  fi
done <<<"$subjects"

if [ "$bad" -ne 0 ]; then
  echo "Expected '<type>[(scope)][!]: <description>', type one of" \
    "feat fix perf refactor docs test build ci chore style revert (see CONTRIBUTING.md)." >&2
fi
exit "$bad"
