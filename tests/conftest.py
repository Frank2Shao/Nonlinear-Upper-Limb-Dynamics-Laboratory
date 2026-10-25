import ipaddress
import socket
from collections.abc import Callable

import pytest
from django.conf import settings


class ExternalNetworkBlocked(RuntimeError):
    """Raised when a test attempts to reach a non-local network host."""


def _allowed_host(host: object) -> bool:
    if host is None:
        return True
    if isinstance(host, bytes):
        host = host.decode("ascii", errors="ignore")
    if not isinstance(host, str):
        return False

    normalized = host.rstrip(".").lower()
    database_host = str(settings.DATABASES["default"].get("HOST", "")).lower()
    if normalized in {"localhost", "testserver", database_host}:
        return True

    try:
        return ipaddress.ip_address(normalized).is_loopback
    except ValueError:
        return False


@pytest.fixture(autouse=True)
def block_external_network(monkeypatch: pytest.MonkeyPatch) -> None:
    """Allow local test services while rejecting outbound test traffic."""
    original_connect: Callable[..., object] = socket.socket.connect
    original_connect_ex: Callable[..., int] = socket.socket.connect_ex
    original_getaddrinfo = socket.getaddrinfo

    def assert_allowed(address: object) -> None:
        if isinstance(address, tuple):
            host = address[0]
        else:
            # Unix-domain socket paths are local and do not contain a host.
            return
        if not _allowed_host(host):
            raise ExternalNetworkBlocked(
                f"External network access is blocked during tests: {host}"
            )

    def guarded_connect(instance, address):
        assert_allowed(address)
        return original_connect(instance, address)

    def guarded_connect_ex(instance, address):
        assert_allowed(address)
        return original_connect_ex(instance, address)

    def guarded_getaddrinfo(host, *args, **kwargs):
        if not _allowed_host(host):
            raise ExternalNetworkBlocked(
                f"External DNS access is blocked during tests: {host}"
            )
        return original_getaddrinfo(host, *args, **kwargs)

    monkeypatch.setattr(socket.socket, "connect", guarded_connect)
    monkeypatch.setattr(socket.socket, "connect_ex", guarded_connect_ex)
    monkeypatch.setattr(socket, "getaddrinfo", guarded_getaddrinfo)
