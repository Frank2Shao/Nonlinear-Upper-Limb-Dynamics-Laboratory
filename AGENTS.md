# Repository Guidelines

## Mandatory Pre-Coding Workflow

Before writing or modifying any code, read `memory-bank/architecture.md` and `memory-bank/design_document.md` in full. Do not rely on summaries or partial excerpts. If either file is missing, inaccessible, or contradictory, stop and ask the project owner before proceeding.

After completing a major feature or milestone, ask the project owner for approval to update `memory-bank/architecture.md`. Do not change architectural decisions silently.

## Project Structure & Module Organization

The repository is at the initial scaffold stage. The planned layout places settings in `config/`, domain applications in `apps/`, shared templates in `templates/`, source assets in `static_src/`, generated assets in `static/`, and tests in `tests/`.

Project references live in `memory-bank/`: `design_document.md`, `tech_stack.md`, `implementation.md`, `项目开发_Roadmap.md`, `architecture.md`, and `progress.md`.

## Build, Test, and Development Commands

These commands apply after the Phase 1 scaffold is created:

- `docker compose up -d`: start PostgreSQL and supporting services.
- `python manage.py migrate`: apply database migrations.
- `python manage.py runserver`: run the local Django server.
- `pytest`: run the automated test suite.
- `ruff check .` and `ruff format --check .`: verify Python quality and formatting.
- `npm run css:watch`: rebuild Tailwind CSS during development.
- `npm run css:build`: generate production CSS.

## Coding Style & Naming Conventions

Use four-space Python indentation and Ruff formatting. Use `snake_case` for functions and modules, `PascalCase` for classes, and descriptive Django URL names such as `events:detail`. Keep business rules in forms, services, models, and database constraints; do not place authorization logic solely in templates, JavaScript, or signals. Name tests `test_<behaviour>.py` and HTMX fragments with a leading underscore.

## Testing Guidelines

Use `pytest` and `pytest-django`. Test normal, invalid, permission, and repeated-submission paths where relevant. Accounts, USU ID validation, privacy boundaries, event registration, and Risk Notice versioning require explicit behavioural assertions. No numeric coverage threshold is established.

## Commit & Pull Request Guidelines

History contains only `Initial commit`, so no convention exists. Use short imperative subjects, preferably `feat:`, `fix:`, `test:`, `docs:`, or `chore:`. Pull requests should explain scope, link the relevant issue or roadmap item, list verification commands, note migrations or configuration changes, and include screenshots for UI changes.

## Security & Configuration

Never commit `.env`, credentials, verification codes, production data, or real member details. Keep secrets in environment variables, provide only safe placeholders in `.env.example`, and use synthetic data in tests and fixtures.
