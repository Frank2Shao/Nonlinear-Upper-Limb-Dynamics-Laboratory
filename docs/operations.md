# Production operations

Day-to-day tasks for the Production server. The one-time server preparation is
in [server-setup.md](server-setup.md).

Unless stated otherwise, run commands on the server as the admin user, in
`/opt/nuldl`. The scripts find `.env.production` and `compose.production.yaml`
there by themselves. For your own Docker commands, add this shortcut to
`~/.bashrc` once:

```bash
alias dc='docker compose --env-file .env.production -f compose.production.yaml'
```

Never paste the contents of `.env.production`, passwords, app passwords or
backup files into a chat, an issue or a commit.

## Deploy a release

Releases are Git tags named `vYYYY.MM.DD` (add `.2`, `.3` for a second release
on the same day). On your own computer, with the release committed and pushed:

```bash
git tag -a v2026.12.01 -m "Short description of the release"
git push origin v2026.12.01
```

On the server:

```bash
scripts/deploy.sh v2026.12.01
```

The script checks out the tag, builds the image, backs up the current state,
applies migrations, sets the Site name and domain, restarts the site and runs
smoke checks. It stops at the first failure and says whether the running site
was changed. Until migrations run, a failure leaves the site as it was.

Each successful deploy adds a line to `deploy.log`: the time, the tag and the
name of the backup taken just before it. The images of the last 3 releases are
kept for rollbacks.

During a deploy the site keeps running; it is unavailable for a few seconds
while the containers restart.

## Roll back

Find the previous release and its backup in `deploy.log`:

```bash
tail -n 3 deploy.log
```

**If the bad release added no migrations**, deploy the previous tag:

```bash
scripts/deploy.sh v2026.11.30
```

**If the bad release added migrations**, the database schema has moved on and
the older code cannot use it. First restore the backup taken just before the bad
release, then deploy the previous tag:

```bash
scripts/restore.sh nuldl-20261201T050000Z
scripts/deploy.sh v2026.11.30
```

Everything written after that backup (new accounts, profile edits,
registrations, avatars) is lost, so roll back this way only when the release
cannot be fixed forward with a new tag.

To see whether a release added migrations, compare the tags on your computer:

```bash
git diff --stat v2026.11.30 v2026.12.01 -- 'apps/*/migrations/'
```

## First admin account

After the first deploy:

```bash
dc exec web python manage.py createsuperuser
```

- Use a long random password from a password manager. The Django Admin sign-in
  page is **not** covered by the site's sign-in rate limits, so a short password
  could be guessed.
- Use the superuser for system settings and emergencies only. For day-to-day
  work, create Staff accounts in Admin → Users and give each only the
  permissions its job needs (for example `Can review USU IDs`, or
  `Can view event registration` for attendance lists).

## Site name and domain

Every deploy sets the Site to the name `NULDL Armwrestling Club` and the domain
from `SITE_DOMAIN`. These appear in email subjects and links. A fresh database
would otherwise say `example.com`. To check:

```bash
dc exec web python manage.py shell -c "from django.contrib.sites.models import Site; print(Site.objects.get_current())"
```

## Change a setting or rotate the Gmail app password

1. For the Gmail app password, create a new one in the club Google Account
   (Security → 2-Step Verification → App passwords).
2. Edit the value on the server: `nano .env.production`.
3. Recreate the web container so it reads the new value:

   ```bash
   dc up -d web
   ```

4. Test email: on the site, request a password reset for an admin account you
   own and confirm the email arrives.
5. Revoke the old app password in the Google Account.

## Logs

```bash
dc logs --tail 100 web
dc logs --since 1h caddy
dc logs --tail 50 db
```

Logs never contain URLs, form data, email addresses or client IP addresses.
Each service keeps at most 3 files of 10 MB; older entries are discarded.
Server errors are also emailed to the `DJANGO_ADMINS` addresses.

## Backups

A backup runs every day at 03:00 and the newest 7 are kept in
`/var/backups/nuldl/`. Each holds the database (`database.dump`) and the avatars
(`media.tar.gz`), and contains real member data.

```bash
tail /var/backups/nuldl/backup.log   # one line per backup: OK or FAILED
ls /var/backups/nuldl/
scripts/backup.sh                    # take one now
```

If the last line of `backup.log` is older than a day or says `FAILED`, check
that the stack is running (`dc ps`) and that the disk is not full (`df -h`).

These backups are on the same server as the site. To survive losing the server,
download a copy every week (next section).

## Download a backup copy (weekly)

On your own computer (PowerShell, macOS or Linux terminal), list the backups and
copy the newest one:

```bash
ssh nuldl@<server> ls /var/backups/nuldl
scp -r nuldl@<server>:/var/backups/nuldl/nuldl-20261207T160000Z <local backup folder>
```

- Keep only the newest 4 copies and delete older ones, so deleted member data
  disappears from every copy within about a month.
- The copies hold real member data. Keep them only on a device with disk
  encryption turned on (BitLocker or FileVault). Do not put them in shared cloud
  folders or send them to anyone.
- To use a copy after losing the server, set up a new server, copy the folder
  into `/var/backups/nuldl/` and follow **Restore a backup**.

## Restore a backup

```bash
scripts/restore.sh nuldl-20261201T160000Z
```

The script checks the backup, asks you to type its name, saves the current state
as `pre-restore-<time>`, replaces the database and avatars, and restarts the
site. The site is unavailable while it runs. If the backup came from an older
release than the one running, run `scripts/deploy.sh <current tag>` afterwards to
apply migrations.

`pre-restore-*` backups are not rotated. Delete them by hand once they are no
longer needed:

```bash
rm -rf /var/backups/nuldl/pre-restore-20261201T161500Z
```

## Delete a member's account

When a member asks through the club's usual channels to have their account
deleted, confirm the request comes from them, then run (replace `USERNAME`):

```bash
dc exec web python manage.py shell -c "
from django.contrib.auth import get_user_model
user = get_user_model().objects.get(username='USERNAME')
profile = getattr(user, 'member_profile', None)
if profile and profile.avatar:
    profile.avatar.delete(save=False)
print(user.delete())
"
```

This removes the account, its email addresses, profile, USYD/USU details and
event registrations, and the avatar file. It cannot be undone.

- Do not delete accounts from Django Admin: that leaves the avatar file in place,
  and anyone who has its link can still open it.
- The signed paper acknowledgement from each session is the record of
  participation; deleting the online registrations does not affect it.
- The data stays in older backups until they rotate out: 7 days on the server,
  about a month in downloaded copies.
- To stop someone from signing in without deleting their data, untick
  **Active** on their account in Django Admin instead.

## Disk space

```bash
df -h /
docker system df
docker builder prune --force   # build cache; it is rebuilt when needed
```
