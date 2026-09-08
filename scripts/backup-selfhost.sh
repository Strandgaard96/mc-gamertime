#!/bin/sh
set -eu

DEST="backups"
KEEP=7

while [ $# -gt 0 ]; do
  case "$1" in
    --dest)
      DEST="$2"
      shift 2
      ;;
    --keep)
      KEEP="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

if [ ! -d config/app ]; then
  echo "config/app not found - run this from the repo root, next to docker-compose.yml" >&2
  exit 1
fi

mkdir -p "$DEST"
STAMP="$(date -u +%Y%m%dT%H%M%S)"
ARCHIVE="$DEST/boardsite-backup-$STAMP.tar.gz"
tar czf "$ARCHIVE" config/app
echo "Backup written to $ARCHIVE"

# shellcheck disable=SC2012
COUNT="$(ls -1 "$DEST"/boardsite-backup-*.tar.gz | wc -l)"
if [ "$COUNT" -gt "$KEEP" ]; then
  PRUNE_COUNT=$((COUNT - KEEP))
  # shellcheck disable=SC2012
  ls -1 "$DEST"/boardsite-backup-*.tar.gz | sort | head -n "$PRUNE_COUNT" | while IFS= read -r old; do
    rm -- "$old"
    echo "Pruned $old"
  done
fi
