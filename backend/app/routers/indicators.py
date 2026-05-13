from __future__ import annotations

from sqlalchemy.orm import Session, aliased
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.deps import require_auth
from app.db import get_db
from app.models import Indicator, Observation, Organ
from app.schemas import (
    IndicatorCreate,
    IndicatorRead,
    IndicatorUpdate,
    OrganCreate,
    OrganRead,
)

router = APIRouter(dependencies=[Depends(require_auth)])


def _escape_ilike(term: str) -> str:
    return term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _to_read(ind: Indicator) -> IndicatorRead:
    return IndicatorRead(
        id=ind.id,
        parent_id=ind.parent_id,
        name=ind.name,
        category=ind.category,
        is_narrative=ind.is_narrative,
        unit=ind.unit,
        ref_range_hint=ind.ref_range_hint,
        organ_ids=[o.id for o in ind.organs],
    )


def _sync_organs(ind: Indicator, organ_ids: List[int], db: Session) -> None:
    if not organ_ids:
        ind.organs.clear()
        return
    organs = db.query(Organ).filter(Organ.id.in_(organ_ids)).all()
    found = {o.id for o in organs}
    missing = set(organ_ids) - found
    if missing:
        raise HTTPException(status_code=400, detail=f"器官 id 不存在: {sorted(missing)}")
    ind.organs = organs


def _assert_no_parent_cycle(db: Session, indicator_id: int, new_parent_id: Optional[int]) -> None:
    if new_parent_id is None:
        return
    cur: Optional[int] = new_parent_id
    while cur is not None:
        if cur == indicator_id:
            raise HTTPException(status_code=400, detail="不能将上级设为自身或其下级")
        row = db.get(Indicator, cur)
        if not row:
            raise HTTPException(status_code=400, detail="上级指标不存在")
        cur = row.parent_id


@router.get("", response_model=List[IndicatorRead])
def list_indicators(
    category: Optional[str] = Query(None, description="physical | lab | imaging"),
    organ_id: Optional[int] = None,
    leaves_only: bool = Query(False, description="仅叶子（可绑定检查值）"),
    search: Optional[str] = Query(
        None,
        description="按名称模糊匹配（适合大量细项时缩小范围）",
    ),
    limit: Optional[int] = Query(
        None,
        ge=1,
        le=10000,
        description="分页大小；不传表示不限制（指标编辑页需要全量时请省略）",
    ),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    q = db.query(Indicator)
    if category:
        q = q.filter(Indicator.category == category)
    if organ_id is not None:
        q = q.join(Indicator.organs).filter(Organ.id == organ_id).distinct()
    if leaves_only:
        child = aliased(Indicator)
        q = (
            q.outerjoin(child, child.parent_id == Indicator.id)
            .filter(child.id.is_(None))
            .distinct()
        )
    if search:
        term = search.strip()
        if term:
            pat = f"%{_escape_ilike(term)}%"
            q = q.filter(Indicator.name.ilike(pat, escape="\\"))
    stmt = q.order_by(Indicator.category.asc(), Indicator.name.asc())
    if limit is not None:
        stmt = stmt.offset(offset).limit(limit)
    rows = stmt.all()
    return [_to_read(ind) for ind in rows]


@router.get("/organs", response_model=List[OrganRead])
def list_organs(db: Session = Depends(get_db)):
    return db.query(Organ).order_by(Organ.sort_order.asc(), Organ.id.asc()).all()


@router.post("/organs", response_model=OrganRead)
def create_organ(body: OrganCreate, db: Session = Depends(get_db)):
    name = body.name.strip()
    if db.query(Organ).filter(Organ.name == name).first():
        raise HTTPException(status_code=400, detail="同名器官已存在")
    o = Organ(
        name=name,
        gender_scope=body.gender_scope,
        sort_order=body.sort_order,
    )
    db.add(o)
    db.commit()
    db.refresh(o)
    return o


@router.post("", response_model=IndicatorRead)
def create_indicator(body: IndicatorCreate, db: Session = Depends(get_db)):
    if body.parent_id is not None:
        p = db.get(Indicator, body.parent_id)
        if not p:
            raise HTTPException(status_code=400, detail="上级指标不存在")
    ind = Indicator(
        name=body.name.strip(),
        category=body.category,
        parent_id=body.parent_id,
        is_narrative=body.is_narrative,
        unit=body.unit,
        ref_range_hint=body.ref_range_hint,
    )
    db.add(ind)
    db.flush()
    _sync_organs(ind, body.organ_ids, db)
    db.commit()
    db.refresh(ind)
    return _to_read(ind)


@router.patch("/{indicator_id}", response_model=IndicatorRead)
def update_indicator(
    indicator_id: int,
    body: IndicatorUpdate,
    db: Session = Depends(get_db),
):
    ind = db.get(Indicator, indicator_id)
    if not ind:
        raise HTTPException(status_code=404, detail="指标不存在")
    data = body.model_dump(exclude_unset=True)
    organ_ids = data.pop("organ_ids", None)
    if "parent_id" in data:
        pid = data["parent_id"]
        if pid is not None:
            par = db.get(Indicator, pid)
            if not par:
                raise HTTPException(status_code=400, detail="上级指标不存在")
        _assert_no_parent_cycle(db, indicator_id, pid)
    for k, v in data.items():
        setattr(ind, k, v)
    if organ_ids is not None:
        _sync_organs(ind, organ_ids, db)
    db.commit()
    db.refresh(ind)
    return _to_read(ind)


@router.delete("/{indicator_id}", status_code=204)
def delete_indicator(indicator_id: int, db: Session = Depends(get_db)):
    ind = db.get(Indicator, indicator_id)
    if not ind:
        raise HTTPException(status_code=404, detail="指标不存在")
    if db.query(Indicator.id).filter(Indicator.parent_id == indicator_id).first():
        raise HTTPException(status_code=409, detail="请先删除或移动下级指标")
    if db.query(Observation.id).filter(Observation.indicator_id == indicator_id).first():
        raise HTTPException(status_code=409, detail="已有检查记录引用该指标，无法删除")
    db.delete(ind)
    db.commit()
    return None
