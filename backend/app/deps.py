from __future__ import annotations

from fastapi import HTTPException, Request


def require_auth(request: Request) -> int:
    """依赖注入：会话中必须已有登录用户。"""
    uid = request.session.get("uid")
    if uid is None:
        raise HTTPException(status_code=401, detail="请先登录")
    return int(uid)
