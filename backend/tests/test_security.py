"""
安全与隐私相关的自动化检查（pytest）。

覆盖：未登录不得访问业务接口、错误口令不得建立会话、登出后失效、伪造 Cookie 无效、
敏感响应防缓存头、公开接口行为等。运行方式见仓库 README 或：

    cd backend && pip install -r requirements-dev.txt && PYTHONPATH=. pytest tests/test_security.py -v
"""

from __future__ import annotations


def test_health_no_auth_required(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


def test_auth_me_without_session_is_not_401(client):
    """会话接口对未登录返回结构化 JSON，不要求 401（与前端 axios 白名单一致）。"""
    r = client.get("/api/auth/me")
    assert r.status_code == 200
    data = r.json()
    assert data.get("authenticated") is False
    assert data.get("user") is None


def test_persons_list_requires_auth(client):
    r = client.get("/api/persons")
    assert r.status_code == 401


def test_indicators_requires_auth(client):
    r = client.get("/api/indicators")
    assert r.status_code == 401


def test_indicators_organs_requires_auth(client):
    r = client.get("/api/indicators/organs")
    assert r.status_code == 401


def test_export_requires_auth(client):
    r = client.get("/api/persons/1/export")
    assert r.status_code == 401


def test_patch_profile_requires_auth(client):
    r = client.patch("/api/auth/profile", json={"username": "hacker"})
    assert r.status_code == 401


def test_wrong_password_no_access(client, admin_creds):
    bad = {**admin_creds, "password": admin_creds["password"] + "_wrong"}
    r = client.post("/api/auth/login", json=bad)
    assert r.status_code == 401
    r2 = client.get("/api/persons")
    assert r2.status_code == 401


def test_login_then_access_then_logout(client, admin_creds):
    r = client.post("/api/auth/login", json=admin_creds)
    assert r.status_code == 200
    assert "fh_session" in r.cookies or r.cookies.get("fh_session") is not None

    r_ok = client.get("/api/persons")
    assert r_ok.status_code == 200

    r_out = client.post("/api/auth/logout")
    assert r_out.status_code == 200

    r_denied = client.get("/api/persons")
    assert r_denied.status_code == 401


def test_tampered_session_cookie_rejected(client, admin_creds):
    client.post("/api/auth/login", json=admin_creds)
    assert client.get("/api/persons").status_code == 200
    # 清空再只带伪造会话，否则会与有效 Cookie 叠加导致仍为 200
    client.cookies.clear()
    client.cookies.set("fh_session", "invalid-signature-or-tampered-payload")
    r = client.get("/api/persons")
    assert r.status_code == 401


def test_api_responses_carry_no_store_cache_headers(logged_in_client):
    r = logged_in_client.get("/api/persons")
    assert r.status_code == 200
    assert "no-store" in (r.headers.get("cache-control") or "").lower()


def test_sqli_style_username_does_not_bypass_auth(client, admin_creds):
    """畸形用户名应无法绕过口令校验（仍为 401）。"""
    evil = {**admin_creds, "username": "admin' OR '1'='1", "password": "nope"}
    assert client.post("/api/auth/login", json=evil).status_code == 401
    assert client.get("/api/persons").status_code == 401


def test_z_rename_profile_keeps_session(logged_in_client, admin_creds):
    """改名后会话仍有效（同一 Cookie）；放在 z_ 测试中，避免先于其它用例改库内用户名。"""
    old_name = admin_creds["username"]
    new_name = old_name + "_renamed"
    r = logged_in_client.patch("/api/auth/profile", json={"username": new_name})
    assert r.status_code == 200
    me = logged_in_client.get("/api/auth/me")
    assert me.json().get("user", {}).get("username") == new_name
    assert logged_in_client.get("/api/persons").status_code == 200
