"""成员自定义头像：磁盘存储（相对 DATA_DIR）。"""

from __future__ import annotations

import shutil
import uuid
from pathlib import Path
from typing import Dict, Optional

from app.db import DATA_DIR

AVATAR_SUBDIR = "avatars"
AVATAR_MAX_BYTES = 2 * 1024 * 1024

MIME_TO_EXT: Dict[str, str] = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}

EXT_TO_MEDIA = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".gif": "image/gif",
}


def person_avatar_dir(person_id: int) -> Path:
    return DATA_DIR / AVATAR_SUBDIR / str(person_id)


def unlink_avatar_file(rel_path: Optional[str]) -> None:
    if not rel_path:
        return
    p = DATA_DIR / rel_path
    try:
        p.unlink(missing_ok=True)
    except OSError:
        pass


def delete_person_avatar_folder(person_id: int) -> None:
    root = person_avatar_dir(person_id)
    if root.is_dir():
        shutil.rmtree(root, ignore_errors=True)


def media_type_for_avatar(rel_path: str) -> str:
    suf = Path(rel_path).suffix.lower()
    return EXT_TO_MEDIA.get(suf, "application/octet-stream")


def save_avatar_upload(person_id: int, content: bytes, content_type: str) -> str:
    """写入磁盘并返回相对 DATA_DIR 的路径 ``avatars/{person_id}/{uuid}.ext``。"""
    ct = (content_type or "").split(";")[0].strip().lower()
    ext = MIME_TO_EXT.get(ct)
    if ext is None:
        raise ValueError("不支持的图片类型")
    if len(content) > AVATAR_MAX_BYTES:
        raise ValueError("头像文件过大")

    d = person_avatar_dir(person_id)
    d.mkdir(parents=True, exist_ok=True)
    fname = f"{uuid.uuid4().hex}{ext}"
    dest = d / fname
    dest.write_bytes(content)
    return f"{AVATAR_SUBDIR}/{person_id}/{fname}"
