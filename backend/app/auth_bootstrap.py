"""启动时初始化 / 按需重置内置管理员账号。"""

from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.auth_password import hash_password
from app.models import AppUser
from app.settings import Settings

_log = logging.getLogger(__name__)


def bootstrap_auth_user(db: Session, settings: Settings) -> None:
    pw_hash = hash_password(settings.fh_admin_password)
    uname = settings.fh_admin_username.strip()
    if not uname:
        raise RuntimeError("FH_ADMIN_USERNAME 不能为空")

    if settings.fh_force_reset_admin:
        row = db.query(AppUser).filter(AppUser.username == uname).one_or_none()
        if row is None:
            db.add(AppUser(username=uname, password_hash=pw_hash))
            db.commit()
            _log.warning(
                "FH_FORCE_RESET_ADMIN：已新建管理员账号 %r（请尽快登录修改口令）",
                uname,
            )
        else:
            row.password_hash = pw_hash
            db.commit()
            _log.warning(
                "FH_FORCE_RESET_ADMIN：已将管理员 %r 的口令重置为环境变量 FH_ADMIN_PASSWORD 或其默认值 "
                "（局域网仍请尽快修改为强口令）",
                uname,
            )
        return

    if db.query(AppUser).first() is not None:
        return

    db.add(AppUser(username=uname, password_hash=pw_hash))
    db.commit()
    _log.info("已创建首个登录账号（用户名 %r），首次部署后建议在界面内修改口令", uname)
