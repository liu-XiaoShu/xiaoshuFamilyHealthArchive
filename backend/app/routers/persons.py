from __future__ import annotations

from collections import defaultdict
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload

from app.current_abnormals import resolve_current_abnormal_for_indicator
from app.deps import require_auth
from app.db import DATA_DIR, get_db
from app.models import ExamSession, Indicator, Observation, Person
from app.organs_catalog import organs_query_filtered_for_person
from app.person_avatar_storage import (
    AVATAR_MAX_BYTES,
    delete_person_avatar_folder,
    media_type_for_avatar,
    save_avatar_upload,
    unlink_avatar_file,
)
from app.person_report_vitals import (
    person_read_payload,
    resolve_report_vitals_batch,
    resolve_report_vitals_for_person,
)
from app.schemas import (
    CurrentAbnormalItem,
    OrganRead,
    PersonCreate,
    PersonRead,
    PersonReadList,
    PersonUpdate,
)

router = APIRouter(dependencies=[Depends(require_auth)])


def _current_indicator_abnormality_counts_for_person_ids(
    db: Session, person_ids: List[int],
) -> tuple[dict[int, int], dict[int, int]]:
    """按成员汇总：每个有观测的指标在自然年规则下为异常或正常。"""
    if not person_ids:
        return {}, {}
    obs_rows = (
        db.query(Observation)
        .join(ExamSession)
        .filter(ExamSession.person_id.in_(person_ids))
        .all()
    )
    groups: dict[tuple[int, int], list[Observation]] = defaultdict(list)
    for o in obs_rows:
        groups[(o.session.person_id, o.indicator_id)].append(o)

    abnormal: dict[int, int] = defaultdict(int)
    normal: dict[int, int] = defaultdict(int)
    for (pid, _ind_id), lst in groups.items():
        is_ab, _wit, _basis = resolve_current_abnormal_for_indicator(lst)
        if is_ab:
            abnormal[pid] += 1
        else:
            normal[pid] += 1
    return abnormal, normal


def _read_person(db: Session, p: Person) -> PersonRead:
    vit = resolve_report_vitals_for_person(db, p.id)
    abnormal_by_pid, normal_by_pid = _current_indicator_abnormality_counts_for_person_ids(db, [p.id])
    return PersonRead(
        **person_read_payload(
            p,
            vit,
            current_abnormal_count=abnormal_by_pid.get(p.id, 0),
            current_normal_indicator_count=normal_by_pid.get(p.id, 0),
        )
    )


@router.get("", response_model=List[PersonReadList])
def list_persons(db: Session = Depends(get_db)):
    persons = db.query(Person).order_by(Person.id.asc()).all()
    if not persons:
        return []

    ids = [p.id for p in persons]
    abnormal_by_pid, normal_by_pid = _current_indicator_abnormality_counts_for_person_ids(db, ids)
    vitals_batch = resolve_report_vitals_batch(db, ids)

    out: List[PersonReadList] = []
    for p in persons:
        data = person_read_payload(
            p,
            vitals_batch[p.id],
            current_abnormal_count=abnormal_by_pid.get(p.id, 0),
            current_normal_indicator_count=normal_by_pid.get(p.id, 0),
        )
        out.append(PersonReadList(**data))
    return out


@router.post("", response_model=PersonRead)
def create_person(body: PersonCreate, db: Session = Depends(get_db)):
    p = Person(**body.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    return _read_person(db, p)


@router.get("/{person_id}/organs", response_model=List[OrganRead])
def list_organs_for_person(person_id: int, db: Session = Depends(get_db)):
    """按成员性别返回适用的器官列表（用于前端分组排序等）；性别未填则返回全部。"""
    p = db.get(Person, person_id)
    if not p:
        raise HTTPException(status_code=404, detail="成员不存在")
    return organs_query_filtered_for_person(db, p).all()


@router.get("/{person_id}/current-abnormals", response_model=List[CurrentAbnormalItem])
def list_current_abnormals_for_person(person_id: int, db: Session = Depends(get_db)):
    """当前仍为异常的细项列表（自然年内复查正常则覆盖；本年无记录则沿用最近异常）。"""
    p = db.get(Person, person_id)
    if not p:
        raise HTTPException(status_code=404, detail="成员不存在")

    obs_rows = (
        db.query(Observation)
        .join(ExamSession)
        .filter(ExamSession.person_id == person_id)
        .options(
            joinedload(Observation.indicator).joinedload(Indicator.parent),
            joinedload(Observation.indicator).joinedload(Indicator.organs),
            joinedload(Observation.session),
        )
        .all()
    )

    by_ind: dict[int, list[Observation]] = defaultdict(list)
    for o in obs_rows:
        by_ind[o.indicator_id].append(o)

    items: List[CurrentAbnormalItem] = []
    for _ind_id, lst in by_ind.items():
        is_ab, wit, basis = resolve_current_abnormal_for_indicator(lst)
        if not is_ab or wit is None:
            continue
        ind = wit.indicator
        par = ind.parent
        items.append(
            CurrentAbnormalItem(
                indicator_id=ind.id,
                indicator_name=ind.name,
                indicator_category=ind.category,
                indicator_is_narrative=ind.is_narrative,
                indicator_parent_name=par.name if par else None,
                basis_label=basis,
                observation_id=wit.id,
                measured_at=wit.measured_at,
                session_report_at=wit.session.report_at,
                value_text=wit.value_text,
                ref_text=wit.ref_text,
                abnormal=wit.abnormal,
                remarks=wit.remarks,
                findings_text=wit.findings_text,
                conclusion_text=wit.conclusion_text,
                organ_names=[org.name for org in ind.organs],
            )
        )

    items.sort(key=lambda x: (x.measured_at, x.indicator_name), reverse=True)
    return items


@router.get("/{person_id}/avatar")
def serve_person_avatar(person_id: int, db: Session = Depends(get_db)):
    """返回成员已上传的头像二进制；未设置或文件缺失时 404。"""
    p = db.get(Person, person_id)
    if not p or not p.avatar_rel_path:
        raise HTTPException(status_code=404, detail="无自定义头像")
    path = DATA_DIR / p.avatar_rel_path
    if not path.is_file():
        raise HTTPException(status_code=404, detail="头像文件缺失")
    return FileResponse(
        path,
        media_type=media_type_for_avatar(p.avatar_rel_path),
        headers={"Cache-Control": "private, no-cache, must-revalidate"},
    )


@router.post("/{person_id}/avatar", response_model=PersonRead)
async def upload_person_avatar(
    person_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    p = db.get(Person, person_id)
    if not p:
        raise HTTPException(status_code=404, detail="成员不存在")
    content = await file.read(AVATAR_MAX_BYTES + 1)
    if len(content) > AVATAR_MAX_BYTES:
        raise HTTPException(status_code=413, detail="头像不超过 2MB")
    try:
        rel = save_avatar_upload(person_id, content, file.content_type or "")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    prev = p.avatar_rel_path
    p.avatar_rel_path = rel
    db.commit()
    db.refresh(p)
    unlink_avatar_file(prev)

    return _read_person(db, p)


@router.delete("/{person_id}/avatar", response_model=PersonRead)
def remove_person_avatar(person_id: int, db: Session = Depends(get_db)):
    p = db.get(Person, person_id)
    if not p:
        raise HTTPException(status_code=404, detail="成员不存在")
    prev = p.avatar_rel_path
    p.avatar_rel_path = None
    db.commit()
    db.refresh(p)
    unlink_avatar_file(prev)
    return _read_person(db, p)


@router.get("/{person_id}", response_model=PersonRead)
def get_person(person_id: int, db: Session = Depends(get_db)):
    p = db.get(Person, person_id)
    if not p:
        raise HTTPException(status_code=404, detail="成员不存在")
    return _read_person(db, p)


@router.patch("/{person_id}", response_model=PersonRead)
def update_person(person_id: int, body: PersonUpdate, db: Session = Depends(get_db)):
    p = db.get(Person, person_id)
    if not p:
        raise HTTPException(status_code=404, detail="成员不存在")
    data = body.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(p, k, v)
    db.commit()
    db.refresh(p)
    return _read_person(db, p)


@router.delete("/{person_id}", status_code=204)
def delete_person(person_id: int, db: Session = Depends(get_db)):
    p = db.get(Person, person_id)
    if not p:
        raise HTTPException(status_code=404, detail="成员不存在")
    delete_person_avatar_folder(person_id)
    db.delete(p)
    db.commit()
    return None
