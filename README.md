# Nonlinear Upper Limb Dynamics Laboratory website

This repository contains the NULDL website and member account system. Phase 1 provides registration, mandatory email verification, password and Magic Code login, account identity management, and USU ID review. Phase 2 adds the English public website. Phase 3 adds member-owned profile editing, original-file Avatar management, Preview, Publish and Unpublish controls, the public Members directory and details, and Admin hide/unhide. Phase 4 adds public Events, member registration and cancellation, versioned Risk Notice confirmation, and a read-only Admin registration list.

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

## Automated acceptance

The Phase 4 acceptance command creates a temporary clean uv environment, installs the locked Python and npm dependencies, starts PostgreSQL, applies migrations, runs the complete shared quality gate, starts the Development server, and runs the Phase 2, Phase 3, and Phase 4 desktop/mobile Playwright smoke tests:

```powershell
python -m uv run --env-file .env python scripts\accept_phase_4.py
```

The shared quality and security gate can be run separately:

```powershell
python -m uv run --env-file .env python scripts\verify_project.py
```

Both commands return a non-zero exit status if any required check fails. Earlier phase commands remain available for historical verification.

### Phase 3 compatibility

The Step 36 acceptance command remains available for the member-profile baseline:

```powershell
python -m uv run --env-file .env python scripts\accept_phase_3.py
```

### Phase 2 compatibility

The Step 28 acceptance command remains available for the public website baseline:

```powershell
python -m uv run --env-file .env python scripts\accept_phase_2.py
```

### Phase 1 compatibility

The Step 20 acceptance command creates a temporary clean uv environment, installs the locked Python and npm dependencies, starts PostgreSQL, applies migrations, runs the complete Phase 1 quality gate, starts the local Django server, and runs desktop and mobile Playwright smoke tests:

```powershell
python -m uv run --env-file .env python scripts\accept_phase_1.py
```

The underlying quality and security gate can be run separately:

```powershell
python -m uv run --env-file .env python scripts\verify_phase_1.py
```

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

## Manual Phase 2 review

Use desktop and mobile-width browsers and review the following without entering real member data:

1. Confirm Home, About, and Beginners & Safety contain the approved English copy and have working Header, Footer, keyboard navigation, visible focus, and no horizontal scrolling.
2. Confirm the Home Logo is sharp and undistorted, and the static session reads `1 December 2026`, `3:00–7:00 pm`, and `Venue details to be confirmed` without registration controls.
3. Confirm the Footer links only to Instagram `@nuldl_armwrestlingclub` and does not publish a contact Email.
4. In Development, confirm Draft Risk Notice displays `DRAFT — NOT APPROVED FOR PARTICIPATION USE`; confirm Production configuration keeps the draft unavailable.
5. Confirm 403, 404, and 500 responses use the project page shell and disclose no traceback, exception details, internal paths, or secrets.
6. Confirm metadata and `/sitemap.xml` include only the approved public pages and exclude authentication, Admin, error, Draft Risk Notice, and future-phase routes.
7. Confirm there are no external fonts or CDN requests, no real member details, and no University logo, crest, or affiliation claim. University branding remains excluded until written approval is recorded.

## Manual Phase 3 review

Use synthetic accounts and temporary media only. Remove the synthetic records and uploaded files after the walkthrough.

1. Register and verify a synthetic member, open **Account**, then follow **Edit profile**.
2. Save each allowed profile field and a synthetic JPG, PNG, or WebP Avatar. Confirm the page warns that original metadata may remain and that saving does not publish the profile.
3. Open **Preview profile** and confirm the public field order, Username URL, Avatar, long Bio wrapping, and safe external social links.
4. Use **Publish profile**, confirm the member appears in **Members**, open the public detail page, then use **Unpublish** and confirm both public routes stop exposing the profile.
5. Replace and remove the Avatar. Confirm old files are removed only after a successful save and failed submissions preserve the current file. Keep all walkthrough uploads in temporary media.
6. In Django Admin, grant a synthetic Staff account the standard MemberProfile change permission. Perform **Admin hide/unhide**, confirm the Admin log entry, and verify that hiding removes the profile from public pages without changing its content, publication preference, or account access.
7. Repeat the main profile and Members paths at desktop and mobile widths using keyboard navigation. Confirm visible focus, associated errors, no horizontal scrolling, and working forms with JavaScript disabled.
8. Confirm public responses contain no Email, USYD declaration, USU ID, review metadata, Executive role, unpublished content, or age/guardian information.

Production media storage remains unresolved and will be selected during Phase 6. Development uses local media; tests and acceptance use isolated temporary media.

## Manual Phase 4 review

Use synthetic accounts, a synthetic Event, a synthetic digits-only USU ID, and a Risk Notice whose first line is `SYNTHETIC TEST ONLY`. Do not enter real member or participant data. Remove the synthetic records after the walkthrough.

1. In Django Admin, create and publish a synthetic Event with future Sydney dates, `registration_open` enabled, venue text, and an optional HTTPS Google Maps URL. Confirm Home shows the Event and **View all events** opens the Upcoming list.
2. Open Upcoming and Past on desktop and mobile widths. Confirm the Event card, detail page, date, time, venue and optional **View location in map** link are readable, and that no **All** filter appears.
3. As an anonymous visitor, confirm the public Event remains visible but registration requires login. Register and verify a synthetic member before continuing.
4. As the verified synthetic member, select **Register**, read the current synthetic Risk Notice, actively confirm it, and verify the page changes to `Registered` without requesting identity details again.
5. Select **Cancel registration**, confirm the cancellation, and verify **Register** returns. Register again and confirm Django Admin retains the cancelled record and the new active record with their accepted Risk Notice versions.
6. Change the current synthetic Risk Notice after opening a registration confirmation page. Submit the stale page and confirm the current version must be reviewed before registration succeeds.
7. Close registration and confirm registration and cancellation controls disappear and direct requests are refused. Move the Event dates into Past and confirm it appears only under Past with no registration controls.
8. Grant a synthetic Staff account only `events.view_eventregistration`. Confirm the registration list is readable but cannot be added to, changed or deleted, and that an unprivileged Staff account cannot open it.
9. Repeat the registration and cancellation flow with JavaScript disabled. Confirm the full confirmation pages, keyboard focus, error messages and mobile layout remain usable without horizontal scrolling.
10. Confirm public Home and Event responses do not expose participant names, Username, Email, USU ID, cancellation history or previous Risk Notice versions.

Production registration remains disabled until the final Risk Notice is approved. Phase 4 Development and test data must remain explicitly synthetic.

## Security and data boundaries

- Never commit `.env`, credentials, verification or login codes, database dumps, real member data, or user uploads.
- Tests and examples use synthetic identities. Phase 1 tests block external network access after dependency and browser installation.
- Email, USU ID, review metadata, unpublished profiles, passwords, codes, and session tokens are private data.
- Production requires independent secrets, hosted PostgreSQL, SMTP, persistent media storage, HTTPS, monitoring, and the remaining provider decisions documented in `memory-bank/`. Production media storage remains unresolved.
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

Phase 4 implementation is undergoing Step 45 acceptance. Current scope and unresolved external decisions are recorded in `memory-bank/progress.md` and `memory-bank/项目开发_Roadmap.md`.
