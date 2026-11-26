#!/usr/bin/env bash
# Back up the Production database and uploaded media.
#
# Run on the server from the repository directory, as a user that can run docker:
#   scripts/backup.sh
# Daily at 3 am (server clock on Australia/Sydney), installed during server setup:
#   0 3 * * * cd /opt/nuldl && scripts/backup.sh >/dev/null
#
# Each run writes BACKUP_DIR/nuldl-<UTC time>/ containing
#   database.dump   pg_dump custom format
#   media.tar.gz    the media volume (avatars)
# keeps the newest KEEP of them, and appends one line to BACKUP_DIR/backup.log
# with the backup size, the size of all backups and the free disk space.
# The backups hold real member data: the directory is readable by its owner only.
#
# BACKUP_KIND=pre-restore (used by restore.sh) names the backup
# pre-restore-<UTC time>/ and leaves it out of the rotation; delete those by hand.
#
# Settings (environment variables):
#   ENV_FILE      default .env.production
#   COMPOSE_FILE  default compose.production.yaml (Docker Compose reads it)
#   BACKUP_DIR    default /var/backups/nuldl
#   KEEP          default 7
set -euo pipefail

ENV_FILE=${ENV_FILE:-.env.production}
export COMPOSE_FILE=${COMPOSE_FILE:-compose.production.yaml}
BACKUP_DIR=${BACKUP_DIR:-/var/backups/nuldl}
KEEP=${KEEP:-7}
BACKUP_KIND=${BACKUP_KIND:-nuldl}

case $BACKUP_KIND in
  nuldl | pre-restore) ;;
  *) echo "BACKUP_KIND must be nuldl or pre-restore" >&2; exit 2 ;;
esac
case $KEEP in
  '' | *[!0-9]* | 0) echo "KEEP must be a positive whole number" >&2; exit 2 ;;
esac

umask 077
mkdir -p "$BACKUP_DIR"
chmod 700 "$BACKUP_DIR"
LOG="$BACKUP_DIR/backup.log"

dc() { docker compose --env-file "$ENV_FILE" "$@"; }
now() { date -u +%Y-%m-%dT%H:%M:%SZ; }

stamp=$(date -u +%Y%m%dT%H%M%SZ)
name="$BACKUP_KIND-$stamp"
partial="$BACKUP_DIR/.partial-$name"
final="$BACKUP_DIR/$name"

finish() {
  status=$?
  if [ "$status" -ne 0 ]; then
    rm -rf -- "$partial"
    echo "$(now) FAILED $name (exit $status)" >>"$LOG"
    echo "Backup failed (exit $status); nothing was kept." >&2
  fi
}
trap finish EXIT

if [ -e "$final" ]; then
  echo "$final already exists" >&2
  exit 1
fi
mkdir "$partial"

# A consistent snapshot even while the site is in use.
dc exec -T db pg_dump -U nuldl -d nuldl --format=custom >"$partial/database.dump"
dc exec -T web tar -C /app/media -czf - . >"$partial/media.tar.gz"

# Only complete backups get their final name, so a failed run is never counted.
mv -T -- "$partial" "$final"

pruned=0
if [ "$BACKUP_KIND" = nuldl ]; then
  shopt -s nullglob
  backups=("$BACKUP_DIR"/nuldl-*/) # glob order is oldest first
  while [ "${#backups[@]}" -gt "$KEEP" ]; do
    rm -rf -- "${backups[0]}"
    backups=("${backups[@]:1}")
    pruned=$((pruned + 1))
  done
fi

size=$(du -sh -- "$final" | cut -f1)
total=$(du -sh -- "$BACKUP_DIR" | cut -f1)
disk=$(df -h --output=avail,pcent -- "$BACKUP_DIR" | tail -n 1 | awk '{print $1 " free, " $2 " used"}')
echo "$(now) OK $name size=$size pruned=$pruned all_backups=$total disk=$disk" >>"$LOG"
echo "$final"
