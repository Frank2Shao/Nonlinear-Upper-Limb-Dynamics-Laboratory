#!/usr/bin/env bash
# Replace the Production database and media with a backup made by backup.sh.
#
# Run on the server from the repository directory:
#   scripts/restore.sh nuldl-20261201T160000Z      (a name in BACKUP_DIR)
#   scripts/restore.sh /path/to/backup-directory
# It asks you to type the backup name; --yes skips that (for rehearsals only).
#
# Order: check the backup can be read; make a pre-restore backup of the current
# state; stop web; drop and recreate the database and load the dump; empty the
# media volume and unpack the archive; start web and wait until it is healthy.
# The database is recreated rather than overwritten, so tables or rows added
# after the backup do not survive. If the backup came from an older release,
# run the deploy (which applies migrations) afterwards.
#
# Uses the same ENV_FILE, COMPOSE_FILE and BACKUP_DIR settings as backup.sh.
set -euo pipefail

ENV_FILE=${ENV_FILE:-.env.production}
export COMPOSE_FILE=${COMPOSE_FILE:-compose.production.yaml}
BACKUP_DIR=${BACKUP_DIR:-/var/backups/nuldl}
export ENV_FILE BACKUP_DIR

usage() { echo "usage: $0 [--yes] <backup name or directory>" >&2; exit 2; }

assume_yes=false
if [ "${1:-}" = --yes ]; then
  assume_yes=true
  shift
fi
[ "$#" -eq 1 ] || usage
case $1 in
  */*) source_dir=${1%/} ;;
  *) source_dir="$BACKUP_DIR/$1" ;;
esac
dump="$source_dir/database.dump"
media="$source_dir/media.tar.gz"
label=$(basename -- "$source_dir")

dc() { docker compose --env-file "$ENV_FILE" "$@"; }

for file in "$dump" "$media"; do
  if [ ! -s "$file" ]; then
    echo "Missing or empty: $file" >&2
    exit 1
  fi
done

echo "Checking the backup can be read..."
dc exec -T db pg_restore --list <"$dump" >/dev/null
tar -tzf - <"$media" >/dev/null

if [ "$assume_yes" != true ]; then
  echo "This replaces ALL current members, events, registrations and avatars with $label."
  read -r -p "Type the backup name to continue: " answer
  if [ "$answer" != "$label" ]; then
    echo "Cancelled; nothing was changed."
    exit 1
  fi
fi

echo "Saving the current state first..."
safety_copy=$(BACKUP_KIND=pre-restore "$(dirname -- "$0")/backup.sh")
echo "Current state saved in $safety_copy"

web_stopped=false
on_exit() {
  status=$?
  if [ "$status" -ne 0 ] && [ "$web_stopped" = true ]; then
    echo "Restore FAILED (exit $status). The web service is stopped." >&2
    echo "To go back: $0 $safety_copy" >&2
  fi
}
trap on_exit EXIT

dc stop web
web_stopped=true

echo "Restoring the database..."
dc exec -T db dropdb -U nuldl --if-exists --force nuldl
dc exec -T db createdb -U nuldl -O nuldl nuldl
dc exec -T db pg_restore -U nuldl -d nuldl --no-owner --exit-on-error --single-transaction <"$dump"

echo "Restoring media..."
# A one-off web container: it runs as the same user that owns the media files.
dc run --rm --no-deps -T web sh -c \
  'find /app/media -mindepth 1 -delete && tar -C /app/media -xzf -' <"$media"

dc start web
web_stopped=false
for _ in $(seq 1 30); do
  if [ "$(dc ps --format '{{.Health}}' web)" = healthy ]; then
    echo "Restored $label; web is healthy."
    exit 0
  fi
  sleep 2
done
echo "Restored $label, but web did not report healthy within 60 seconds." >&2
echo "Check: docker compose --env-file $ENV_FILE logs web" >&2
exit 1
