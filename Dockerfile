# Production image. Base images are pinned by digest; update tag and digest together.
FROM python:3.13.17-slim-trixie@sha256:d98cc29d3266e535dd9da1099688d9cb3ca4753813571e071763d17725460962 AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

FROM base AS dependencies
ENV UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never
RUN pip install --no-cache-dir --disable-pip-version-check uv==0.13.5
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

FROM base
ENV PATH="/app/.venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=config.settings.production
RUN useradd --uid 10001 --user-group --no-create-home --shell /usr/sbin/nologin app
COPY --from=dependencies /app/.venv /app/.venv
COPY manage.py ./
COPY apps ./apps
COPY config ./config
COPY templates ./templates
COPY static ./static
# Production settings require these values to load; none of them stays in the image.
RUN DJANGO_SECRET_KEY=build-only-placeholder \
    DJANGO_ALLOWED_HOSTS=build.invalid \
    DJANGO_CSRF_TRUSTED_ORIGINS=https://build.invalid \
    DATABASE_URL=postgresql://build:build@build.invalid:5432/build \
    EMAIL_HOST=build.invalid \
    EMAIL_PORT=587 \
    EMAIL_HOST_USER=build-placeholder \
    EMAIL_HOST_PASSWORD=build-placeholder \
    EMAIL_USE_TLS=true \
    DEFAULT_FROM_EMAIL=build@build.invalid \
    python manage.py collectstatic --noinput --verbosity 0
# New named volumes copy the ownership of these directories.
RUN install -d -o app -g app /app/media /srv/static
USER app
EXPOSE 8000
CMD ["gunicorn", "--config", "config/gunicorn.conf.py", "config.wsgi:application"]
