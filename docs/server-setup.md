# Server setup checklist

One-time preparation of the Production server: a BinaryLane VPS in Sydney with
at least 1 GB of memory and a public IPv4 address, running Ubuntu 24.04 LTS.
Work through the sections in order. Day-to-day tasks (deploying, rolling back,
backups, logs, the first admin account) are in [operations.md](operations.md).

Never paste the contents of `.env.production`, passwords or app passwords into a
chat, an issue or a commit.

## 1. Before you start

- When creating the VPS, choose Ubuntu 24.04 LTS and add your SSH **public** key
  so the first login does not need a password.
- Point the domain at the server with an **A record only** (IPv4). Do not add an
  AAAA record: Docker would report every IPv6 visitor with the same address,
  which breaks the per-visitor sign-in limits.
- Have the club Gmail app password ready (Google Account → Security → 2-Step
  Verification → App passwords). It is entered on the server in step 9, not here.

## 2. Admin user

Log in as `root` once, then create a personal admin user (here `nuldl`) and copy
the SSH key to it:

```bash
adduser nuldl
usermod -aG sudo nuldl
rsync --archive --chown=nuldl:nuldl ~/.ssh /home/nuldl
```

Log out and log back in as `nuldl`. All later commands run as this user.

## 3. SSH: keys only, no root login

Keep the current session open until a new login has worked.

```bash
sudo tee /etc/ssh/sshd_config.d/10-nuldl.conf >/dev/null <<'EOF'
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitRootLogin no
EOF
sudo sshd -t && sudo systemctl reload ssh
```

Open a second terminal and confirm `ssh nuldl@<server>` still works.

## 4. Firewall: only 22, 80 and 443

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status
```

Ports that Docker publishes bypass ufw. The Production stack publishes only
80 and 443; the database is reachable from the other containers only.

## 5. Automatic security updates

```bash
sudo apt update && sudo apt full-upgrade -y
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -f noninteractive unattended-upgrades
sudo tee /etc/apt/apt.conf.d/52nuldl-reboot >/dev/null <<'EOF'
Unattended-Upgrade::Automatic-Reboot "true";
Unattended-Upgrade::Automatic-Reboot-Time "04:30";
EOF
```

When an update needs a reboot, the server restarts at 04:30, after the 03:00
backup. The containers start again by themselves.

## 6. Time zone

The daily backup runs at 03:00 by the server clock, so the clock must be on
Sydney time:

```bash
sudo timedatectl set-timezone Australia/Sydney
timedatectl
```

## 7. Swap (2 GB)

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
free -h
```

## 8. Docker

Install Docker Engine and the Compose plugin from Docker's own repository
(the steps at https://docs.docker.com/engine/install/ubuntu/):

```bash
sudo apt install -y ca-certificates curl git
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" |
  sudo tee /etc/apt/sources.list.d/docker.list >/dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker nuldl
```

Log out and back in, then check `docker compose version`. Membership of the
`docker` group is equivalent to root access; give it only to server admins.

## 9. Code and configuration

```bash
sudo install -d -o nuldl -g nuldl /opt/nuldl
git clone <repository URL> /opt/nuldl
cd /opt/nuldl
cp .env.production.example .env.production
chmod 600 .env.production
nano .env.production
```

- If the repository is private, add a read-only deploy key for the server
  (GitHub → repository Settings → Deploy keys) and clone with the SSH URL.
- Fill in every value in `.env.production` on the server itself; the example file
  explains how to generate each one. Keep the file only here.

## 10. Backup directory

```bash
sudo install -d -m 700 -o nuldl -g nuldl /var/backups/nuldl
```

## 11. First deploy

Follow **Deploy a release** in [operations.md](operations.md). The first deploy
takes no backup because there is nothing to back up yet. Then create the first
admin account (**First admin account** in the same file).

## 12. Daily backup

As `nuldl`, run `crontab -e` and add:

```text
0 3 * * * cd /opt/nuldl && scripts/backup.sh >/dev/null
```

The next morning, `tail /var/backups/nuldl/backup.log` should show an `OK` line.

## 13. Final checks

- [ ] `ssh root@<server>` and password logins are refused.
- [ ] `sudo ufw status` lists only OpenSSH, 80 and 443.
- [ ] `timedatectl` shows `Australia/Sydney`; `free -h` shows 2 GB swap.
- [ ] `ls -l /opt/nuldl/.env.production` shows `-rw-------`.
- [ ] `ls -ld /var/backups/nuldl` shows `drwx------`.
- [ ] The site opens over HTTPS with a valid certificate.
- [ ] After the first night, `backup.log` has an `OK` line.
