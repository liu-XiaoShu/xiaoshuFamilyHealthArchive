"""应用配置（环境变量前缀 FH_）。

生产环境请务必设置较长的 FH_SESSION_SECRET。默认管理员口令仅适合开发与首次引导。
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    fh_session_secret: str = Field(
        default="dev-only-fh-session-secret-replace-me-please",
        description="会话 Cookie 签名密钥",
    )
    fh_admin_username: str = Field(default="admin")
    fh_admin_password: str = Field(default="family-health")
    fh_force_reset_admin: bool = Field(default=False)

    @field_validator("fh_force_reset_admin", mode="before")
    @classmethod
    def _coerce_bool(cls, v: object) -> bool:
        if isinstance(v, bool):
            return v
        if v is None:
            return False
        s = str(v).strip().lower()
        return s in ("1", "true", "yes", "on")

    @field_validator("fh_session_secret")
    @classmethod
    def _warn_short_secret(cls, v: str) -> str:
        if len(v) < 16:
            raise ValueError("FH_SESSION_SECRET 长度至少应为 16 位")
        return v


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
