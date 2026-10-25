import pytest
from django.core.exceptions import ImproperlyConfigured

from config.settings.base import database_from_url, required_env


def test_database_url_builds_postgresql_settings() -> None:
    database = database_from_url(
        "postgresql://example%20user:example%2Fpassword@db.example.test:5433/"
        "nuldl?sslmode=require"
    )

    assert database == {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "nuldl",
        "USER": "example user",
        "PASSWORD": "example/password",
        "HOST": "db.example.test",
        "PORT": "5433",
        "OPTIONS": {"sslmode": "require"},
    }


def test_database_url_rejects_non_postgresql_backend() -> None:
    with pytest.raises(ImproperlyConfigured, match="must use PostgreSQL"):
        database_from_url("sqlite:///local.sqlite3")


def test_required_environment_variable_fails_clearly(monkeypatch) -> None:
    variable_name = "NULDL_TEST_REQUIRED_ENV"
    monkeypatch.delenv(variable_name, raising=False)

    with pytest.raises(ImproperlyConfigured, match=variable_name):
        required_env(variable_name)
