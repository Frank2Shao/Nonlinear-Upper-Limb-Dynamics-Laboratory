# Nonlinear Upper Limb Dynamics Laboratory website

This repository contains the NULDL website and member account system. Phase 1 provides registration, mandatory email verification, password and Magic Code login, account identity management, USU ID review in Django Admin, and a responsive local-asset interface.

NULDL uses neutral project branding. This repository does not claim to be an official University of Sydney website and does not include University logos, crests, or other unapproved brand assets.

## Requirements

- Python 3.13
- uv
- Node.js and npm
- Docker with Docker Compose

Verify the tools before setup:

```powershell
python --version
uv --version
node --version
npm.cmd --version
docker compose version
```

## First-time local setup

Run these commands from the repository root in PowerShell:

```powershell
Copy-Item .env.example .env
python -m uv sync --locked
npm.cmd ci
docker compose up -d --wait postgres
python -m uv run --env-file .env python manage.py migrate
npm.cmd run static:build
python -m uv run --env-file .env python manage.py runserver
```

Open <http://127.0.0.1:8000/>. Development email is written to the Django terminal by the console email backend; no external SMTP service is required.

The `.env` file contains local configuration and must remain untracked. Replace its development-only values before any non-local deployment.

## Daily development

Start PostgreSQL and the Tailwind watcher in separate terminals:

```powershell
docker compose up -d --wait postgres
npm.cmd run css:watch
```

Run Django in another terminal:

```powershell
python -m uv run --env-file .env python manage.py runserver
```

Apply migrations after pulling schema changes:

```powershell
python -m uv run --env-file .env python manage.py migrate
```

## Automated Phase 1 acceptance

The Step 20 acceptance command creates a temporary clean uv environment, installs the locked Python and npm dependencies, starts PostgreSQL, applies migrations, runs the complete Phase 1 quality gate, starts the local Django server, and runs desktop and mobile Playwright smoke tests:

```powershell
python -m uv run --env-file .env python scripts\accept_phase_1.py
```

The underlying quality and security gate can be run separately:

```powershell
python -m uv run --env-file .env python scripts\verify_phase_1.py
```

Both commands return a non-zero exit status if any required check fails.

## Manual Phase 1 walkthrough

Use synthetic identities only. Do not enter real member details or real USU IDs.

1. Start the local server and open <http://127.0.0.1:8000/> on desktop and at a mobile-width viewport.
2. Select **Join the Club**, register with a synthetic Username and an `example.net` Email, and optionally submit a digits-only synthetic USU ID after selecting the USYD student checkbox.
3. Copy the email verification code from the development server terminal, confirm it, and verify that the Account page opens with the USU status shown as `Pending` when an ID was submitted.
4. Use **Log out** and confirm the POST action returns to Home. A direct GET to the logout page must only show confirmation and must not end the session.
5. Log in again with Username and Password, update the USYD declaration or synthetic USU ID, and confirm the success message and expected review state.
6. Log out, choose **Log in by email code**, obtain the Magic Code from the development server terminal, confirm it, and verify that Account opens.
7. Create a local administrator if required:

   ```powershell
   python -m uv run --env-file .env python manage.py createsuperuser
   ```

8. Open <http://127.0.0.1:8000/admin/>, select the synthetic pending submission, run **Mark selected USU IDs as verified**, and confirm the member Account page shows `Verified` without exposing reviewer details.
9. Confirm keyboard navigation, visible focus, error association, code paste, and absence of horizontal scrolling on desktop and mobile widths.
10. Confirm pages use NULDL-only branding and contain no University logo, crest, or official-affiliation claim.

## Security and data boundaries

- Never commit `.env`, credentials, verification or login codes, database dumps, real member data, or user uploads.
- Tests and examples use synthetic identities. Phase 1 tests block external network access after dependency and browser installation.
- Email, USU ID, review metadata, unpublished profiles, passwords, codes, and session tokens are private data.
- Production requires independent secrets, hosted PostgreSQL, SMTP, persistent media storage, HTTPS, monitoring, and the remaining provider decisions documented in `memory-bank/`.
- University branding remains excluded until written approval is recorded.

## Project structure

- `apps/`: Django domain applications
- `config/`: URLs and environment-specific settings
- `templates/`: project-level authentication templates
- `static_src/`: Tailwind source
- `static/`: generated and vendored browser assets
- `tests/`: model, form, integration, security, and Playwright tests
- `scripts/`: asset, quality-gate, and acceptance tooling
- `memory-bank/`: product, architecture, implementation, roadmap, and progress records

Phase 2 has not started. Current scope and unresolved external decisions are recorded in `memory-bank/progress.md` and `memory-bank/项目开发_Roadmap.md`.
