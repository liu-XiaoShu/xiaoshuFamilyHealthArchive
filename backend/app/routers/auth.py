from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.auth_password import verify_password
from app.db import get_db
from app.deps import require_auth
from app.models import AppUser
from app.schemas import LoginBody, UsernameUpdate

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login")
async def login(
    request: Request,
    body: LoginBody,
    db: Session = Depends(get_db),
):
    row = db.query(AppUser).filter(AppUser.username == body.username.strip()).one_or_none()
    if row is None or not verify_password(body.password, row.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码不正确")
    request.session.clear()
    request.session["uid"] = row.id
    request.session["username"] = row.username
    return {"ok": True, "user": {"username": row.username}}


@router.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return {"ok": True}


@router.get("/me")
async def auth_me(request: Request) -> dict:
    if request.session.get("uid") is None:
        return {"authenticated": False, "user": None}
    name = request.session.get("username")
    return {"authenticated": True, "user": {"username": str(name)}}


@router.patch("/profile")
async def patch_profile_username(
    request: Request,
    body: UsernameUpdate,
    db: Session = Depends(get_db),
    uid: int = Depends(require_auth),
):
    new_name = body.username.strip()
    if not new_name:
        raise HTTPException(status_code=400, detail="用户名不能为空")

    row = db.query(AppUser).filter(AppUser.id == uid).one_or_none()
    if row is None:
        raise HTTPException(status_code=401, detail="会话无效，请重新登录")

    taken = (
        db.query(AppUser)
        .filter(AppUser.username == new_name, AppUser.id != uid)
        .one_or_none()
    )
    if taken is not None:
        raise HTTPException(status_code=400, detail="该用户名已被使用")

    row.username = new_name
    db.commit()
    request.session["username"] = new_name
    return {"ok": True, "user": {"username": new_name}}
