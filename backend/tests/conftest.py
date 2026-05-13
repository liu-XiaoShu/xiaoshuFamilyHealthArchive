"""安全与认证相关测试：必须在 import app 之前固定独立 SQLite，避免碰生产/开发库。"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

_fd, _SECURITY_TEST_DB = tempfile.mkstemp(prefix="fh_security_", suffix=".db")
os.close(_fd)
_SECURITY_TEST_DB_PATH = Path(_SECURITY_TEST_DB)

os.environ["FH_TEST_DATABASE_URL"] = f"sqlite:///{_SECURITY_TEST_DB_PATH}"
os.environ.setdefault("FH_ADMIN_USERNAME", "security_test_user")
os.environ.setdefault("FH_ADMIN_PASSWORD", "Security-Test-Passphrase-One-9!")
# 满足 Settings 校验：至少 16 字符
os.environ.setdefault("FH_SESSION_SECRET", "fh-security-pytest-session-secret-32")


def pytest_sessionfinish(session, exitstatus) -> None:
    try:
        _SECURITY_TEST_DB_PATH.unlink(missing_ok=True)
    except OSError:
        pass


@pytest.fixture
def client():
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture
def admin_creds() -> dict[str, str]:
    return {
        "username": os.environ["FH_ADMIN_USERNAME"],
        "password": os.environ["FH_ADMIN_PASSWORD"],
    }


@pytest.fixture
def logged_in_client(client, admin_creds):
    r = client.post("/api/auth/login", json=admin_creds)
    assert r.status_code == 200
    return client
