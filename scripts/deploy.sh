#!/usr/bin/env bash
# Deploy a tagged release of the website to the Production stack.
#
# Run on the server from the repository directory (see docs/operations.md):
#   scripts/deploy.sh v2026.12.01
#
# Steps, stopping at the first failure:
#   1. check the working tree has no local changes, fetch tags, check out the tag
#   2. build the image nuldl-website:<tag>
#   3. back up the database and media (skipped on the very first deploy)
#   4. apply migrations and run Django's deploy checks with the new image
#   5. set the Site name and domain (used in email subjects and links)
#   6. tag the image as nuldl-website:current and restart the stack with it
#   7. wait until web is healthy and run smoke checks through Caddy
#   8. record the release in deploy.log and remove images older than the last 3
# Until step 4 the running site is untouched. To roll back, see docs/operations.md.
#
# Settings (environment variables):
#   ENV_FILE          default .env.production
#   COMPOSE_FILE      default compose.production.yaml (Docker Compose reads it)
#   BACKUP_DIR        default /var/backups/nuldl (passed on to backup.sh)
#   HTTPS_PORT        default 443, the port the smoke checks connect to
#   SMOKE_TLS_VERIFY  default yes; "no" accepts an untrusted certificate (rehearsals only)
set -euo pipefail

ENV_FILE=${ENV_FILE:-.env.production}
export COMPOSE_FILE=${COMPOSE_FILE:-compose.production.yaml}
export ENV_FILE
HTTPS_PORT=${HTTPS_PORT:-443}
SMOKE_TLS_VERIFY=${SMOKE_TLS_VERIFY:-yes}
DEPLOY_LOG=deploy.log
IMAGE=nuldl-website
KEEP_IMAGES=3
SITE_NAME="NULDL Armwrestling Club"

dc() { docker compose --env-file "$ENV_FILE" "$@"; }
now() { date -u +%Y-%m-%dT%H:%M:%SZ; }
say() { echo "== $*"; }

stage="checking"
previous=""
backup_name=""

on_exit() {
  status=$?
  [ "$status" -eq 0 ] && return
  echo "Deploy FAILED while $stage (exit $status)." >&2
  case $stage in
    checking | building | "backing up")
      echo "The running site was not changed." >&2 ;;
    migrating | "configuring the site")
      echo "The running site still uses the previous image, but migrations may have run." >&2
      [ -n "$backup_name" ] && echo "To undo them: scripts/restore.sh $backup_name" >&2 ;;
    *)
      echo "The site may be running the new release in a broken state." >&2
      [ -n "$previous" ] && echo "To go back: see Roll back in docs/operations.md (previous release $previous, backup ${backup_name:-none})." >&2 ;;
  esac
}

smoke() {
  local domain=$1 base body home css
  local curl=(curl -sS --max-time 15 --resolve "$domain:$HTTPS_PORT:127.0.0.1")
  [ "$SMOKE_TLS_VERIFY" = no ] && curl+=(-k)
  base="https://$domain:$HTTPS_PORT"
  expect() { # expect <status> <path>
    local got
    got=$("${curl[@]}" -w '\n%{http_code}' "$base$2" | tail -n 1)
    if [ "$got" != "$1" ]; then
      echo "smoke: $2 returned $got, expected $1" >&2
      return 1
    fi
    echo "smoke: $2 -> $got"
  }
  body=$("${curl[@]}" "$base/health/")
  [ "$body" = '{"status": "ok"}' ] || { echo "smoke: /health/ said $body" >&2; return 1; }
  echo "smoke: /health/ -> ok"
  expect 200 /
  home=$("${curl[@]}" "$base/")
  css=$(grep -o '/static/css/site\.[0-9a-f]*\.css' <<<"$home" | head -n 1 || true)
  [ -n "$css" ] || { echo "smoke: no hashed stylesheet on the home page" >&2; return 1; }
  expect 200 "$css"
  expect 200 /admin/login/
  expect 404 /risk-notice/
}

main() {
  [ "$#" -eq 1 ] || { echo "usage: $0 <release tag>" >&2; exit 2; }
  local tag=$1 domain
  trap on_exit EXIT

  [ -f "$ENV_FILE" ] || { echo "Missing $ENV_FILE" >&2; exit 1; }
  domain=$(sed -n 's/^SITE_DOMAIN=//p' "$ENV_FILE" | tail -n 1)
  [ -n "$domain" ] || { echo "SITE_DOMAIN is not set in $ENV_FILE" >&2; exit 1; }
  if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
    echo "The repository has local changes; deploy only committed, tagged releases." >&2
    git status --short --untracked-files=no >&2
    exit 1
  fi
  [ -f "$DEPLOY_LOG" ] && previous=$(tail -n 1 "$DEPLOY_LOG" | awk '{print $2}')

  say "fetching $tag"
  git fetch --quiet --tags origin
  git rev-parse --quiet --verify "refs/tags/$tag^{commit}" >/dev/null ||
    { echo "No such tag: $tag" >&2; exit 1; }
  local old_head
  old_head=$(git rev-parse HEAD)
  git -c advice.detachedHead=false checkout --quiet --detach "refs/tags/$tag"

  stage="building"
  say "building $IMAGE:$tag"
  IMAGE_TAG=$tag dc build --quiet web

  stage="backing up"
  dc up -d --wait db
  if [ -n "$(dc ps --status running --quiet web)" ]; then
    say "backing up the current state"
    backup_name=$(basename -- "$(scripts/backup.sh)")
    echo "backup: $backup_name"
  else
    say "web is not running (first deploy?): no backup taken"
  fi

  stage="migrating"
  say "applying migrations"
  IMAGE_TAG=$tag dc run --rm --no-deps -T web python manage.py migrate --noinput
  IMAGE_TAG=$tag dc run --rm --no-deps -T web python manage.py check --deploy --fail-level WARNING

  stage="configuring the site"
  IMAGE_TAG=$tag dc run --rm --no-deps -T web python manage.py shell -c "
import os
from django.conf import settings
from django.contrib.sites.models import Site
Site.objects.update_or_create(
    id=settings.SITE_ID,
    defaults={'domain': os.environ['DJANGO_ALLOWED_HOSTS'], 'name': '$SITE_NAME'},
)"

  stage="restarting"
  say "starting $tag"
  docker tag "$IMAGE:$tag" "$IMAGE:current"
  dc up -d --remove-orphans
  # Caddy reads its config file at start; restart it when the release changed it.
  if ! git diff --quiet "$old_head" HEAD -- Caddyfile; then
    dc up -d --no-deps --force-recreate caddy
  fi

  stage="checking the new release"
  local healthy=false
  for _ in $(seq 1 45); do
    if [ "$(dc ps --format '{{.Health}}' web)" = healthy ]; then
      healthy=true
      break
    fi
    sleep 2
  done
  [ "$healthy" = true ] || { echo "web did not report healthy within 90 seconds" >&2; exit 1; }
  smoke "$domain"

  stage="recording"
  echo "$(now) $tag backup=${backup_name:-none}" >>"$DEPLOY_LOG"
  local keep old
  keep=$(tail -n "$KEEP_IMAGES" "$DEPLOY_LOG" | awk '{print $2}')
  for old in $(docker image ls "$IMAGE" --format '{{.Tag}}'); do
    [ "$old" = current ] && continue
    grep -qxF -- "$old" <<<"$keep" || docker image rm "$IMAGE:$old" >/dev/null || true
  done
  docker image prune --force >/dev/null

  say "deployed $tag (previous release: ${previous:-none})"
}

# One line, so bash has read all of it before checkout replaces this file.
main "$@"; exit $?
