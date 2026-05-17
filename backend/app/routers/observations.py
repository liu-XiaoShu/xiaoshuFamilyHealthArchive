from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.deps import require_auth
from app.db import get_db
from app.indicator_helpers import assert_indicator_is_leaf
from app.models import ExamSession, Observation, Person
from app.schemas import ObservationCreateItem, ObservationRead, ObservationUpdate

router = APIRouter(dependencies=[Depends(require_auth)])


def _to_read(obs: Observation) -> ObservationRead:
    ind = obs.indicator
    organs = ind.organs
    par = ind.parent
    return ObservationRead(
        id=obs.id,
        session_id=obs.session_id,
        indicator_id=obs.indicator_id,
        measured_at=obs.measured_at,
        value_text=obs.value_text,
        ref_text=obs.ref_text,
        abnormal=obs.abnormal,
        remarks=obs.remarks,
        findings_text=obs.findings_text,
        conclusion_text=obs.conclusion_text,
        indicator_name=ind.name,
        indicator_category=ind.category,
        indicator_is_narrative=ind.is_narrative,
        indicator_parent_id=par.id if par else None,
        indicator_parent_name=par.name if par else None,
        indicator_unit=ind.unit,
        indicator_ref_range_hint=ind.ref_range_hint,
        organ_ids=[o.id for o in organs],
        organ_names=[o.name for o in organs],
        session_report_at=obs.session.report_at,
    )


@router.get("/{person_id}/observations", response_model=List[ObservationRead])
def list_observations_for_person(
    person_id: int,
    view: Optional[str] = Query(None, description="organ | type | timeline，仅前端分组用"),
    time_from: Optional[datetime] = Query(None, alias="from"),
    time_to: Optional[datetime] = Query(None, alias="to"),
    db: Session = Depends(get_db),
):
    _ = view
    person = db.get(Person, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="成员不存在")
    q = (
        db.query(Observation)
        .join(ExamSession)
        .filter(ExamSession.person_id == person_id)
    )
    if time_from is not None:
        q = q.filter(Observation.measured_at >= time_from)
    if time_to is not None:
        q = q.filter(Observation.measured_at <= time_to)
    q = q.order_by(Observation.measured_at.desc(), Observation.id.desc())
    rows = q.all()
    return [_to_read(o) for o in rows]


batch_router = APIRouter(
    prefix="/api/persons/{person_id}/sessions/by-id/{session_id}",
    tags=["observations"],
    dependencies=[Depends(require_auth)],
)


def _get_session_or_404(person_id: int, session_id: int, db: Session) -> ExamSession:
    person = db.get(Person, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="成员不存在")
    session = db.get(ExamSession, session_id)
    if not session or session.person_id != person_id:
        raise HTTPException(status_code=404, detail="报告批次不存在")
    return session


def _get_observation_or_404(
    person_id: int,
    session_id: int,
    observation_id: int,
    db: Session,
) -> Observation:
    _get_session_or_404(person_id, session_id, db)
    obs = db.get(Observation, observation_id)
    if not obs or obs.session_id != session_id:
        raise HTTPException(status_code=404, detail="观测记录不存在")
    return obs


@batch_router.post("/observations", response_model=List[ObservationRead])
def batch_create_observations(
    person_id: int,
    session_id: int,
    body: List[ObservationCreateItem],
    db: Session = Depends(get_db),
):
    if not body:
        return []
    session = _get_session_or_404(person_id, session_id, db)

    created: List[Observation] = []
    for item in body:
        assert_indicator_is_leaf(db, item.indicator_id)
        measured = item.measured_at or session.report_at
        obs = Observation(
            session_id=session_id,
            indicator_id=item.indicator_id,
            measured_at=measured,
            value_text=item.value_text,
            ref_text=item.ref_text,
            abnormal=item.abnormal,
            remarks=item.remarks,
            findings_text=item.findings_text,
            conclusion_text=item.conclusion_text,
        )
        db.add(obs)
        created.append(obs)
    db.commit()
    for o in created:
        db.refresh(o)
    return [_to_read(o) for o in created]


@batch_router.get("/observations", response_model=List[ObservationRead])
def list_session_observations(
    person_id: int,
    session_id: int,
    db: Session = Depends(get_db),
):
    _get_session_or_404(person_id, session_id, db)
    rows = (
        db.query(Observation)
        .filter(Observation.session_id == session_id)
        .order_by(Observation.measured_at.desc(), Observation.id.desc())
        .all()
    )
    return [_to_read(o) for o in rows]


@batch_router.patch("/observations/{observation_id}", response_model=ObservationRead)
def update_observation(
    person_id: int,
    session_id: int,
    observation_id: int,
    body: ObservationUpdate,
    db: Session = Depends(get_db),
):
    session = _get_session_or_404(person_id, session_id, db)
    obs = _get_observation_or_404(person_id, session_id, observation_id, db)
    data = body.model_dump(exclude_unset=True)
    if not data:
        return _to_read(obs)
    if "indicator_id" in data:
        assert_indicator_is_leaf(db, data["indicator_id"])
        obs.indicator_id = data["indicator_id"]
    if "measured_at" in data:
        obs.measured_at = data["measured_at"] or session.report_at
    for field in ("value_text", "ref_text", "abnormal", "remarks", "findings_text", "conclusion_text"):
        if field in data:
            setattr(obs, field, data[field])
    db.commit()
    db.refresh(obs)
    return _to_read(obs)


@batch_router.delete("/observations/{observation_id}", status_code=204)
def delete_observation(
    person_id: int,
    session_id: int,
    observation_id: int,
    db: Session = Depends(get_db),
):
    obs = _get_observation_or_404(person_id, session_id, observation_id, db)
    db.delete(obs)
    db.commit()
