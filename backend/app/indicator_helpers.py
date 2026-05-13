from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Indicator


def assert_indicator_is_leaf(db: Session, indicator_id: int) -> Indicator:
    ind = db.get(Indicator, indicator_id)
    if not ind:
        raise HTTPException(status_code=404, detail="指标不存在")
    has_child = (
        db.query(Indicator.id).filter(Indicator.parent_id == indicator_id).first()
    )
    if has_child:
        raise HTTPException(
            status_code=400,
            detail="只能选择具体检查细项录入，不能选择分组节点",
        )
    return ind
