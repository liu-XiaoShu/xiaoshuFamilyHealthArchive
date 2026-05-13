from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.deps import require_auth
from app.db import get_db
from app.models import ExamSession, Person
from app.schemas import ExamSessionCreate, ExamSessionRead, ExamSessionUpdate

router = APIRouter(dependencies=[Depends(require_auth)])


def _session_or_404(db: Session, session_id: int) -> ExamSession:
    s = db.get(ExamSession, session_id)
    if not s:
        raise HTTPException(status_code=404, detail="报告批次不存在")
    return s


@router.get("", response_model=List[ExamSessionRead])
def list_sessions_for_person(person_id: int, db: Session = Depends(get_db)):
    person = db.get(Person, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="成员不存在")
    q = (
        db.query(ExamSession)
        .filter(ExamSession.person_id == person_id)
        .order_by(ExamSession.report_at.desc())
    )
    return q.all()


@router.post("", response_model=ExamSessionRead)
def create_session(person_id: int, body: ExamSessionCreate, db: Session = Depends(get_db)):
    person = db.get(Person, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="成员不存在")
    s = ExamSession(person_id=person_id, **body.model_dump())
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


@router.get("/by-id/{session_id}", response_model=ExamSessionRead)
def get_session(person_id: int, session_id: int, db: Session = Depends(get_db)):
    s = _session_or_404(db, session_id)
    if s.person_id != person_id:
        raise HTTPException(status_code=404, detail="报告批次不存在")
    return s


@router.patch("/by-id/{session_id}", response_model=ExamSessionRead)
def update_session(
    person_id: int,
    session_id: int,
    body: ExamSessionUpdate,
    db: Session = Depends(get_db),
):
    s = _session_or_404(db, session_id)
    if s.person_id != person_id:
        raise HTTPException(status_code=404, detail="报告批次不存在")
    data = body.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(s, k, v)
    db.commit()
    db.refresh(s)
    return s


@router.delete("/by-id/{session_id}", status_code=204)
def delete_session(person_id: int, session_id: int, db: Session = Depends(get_db)):
    s = _session_or_404(db, session_id)
    if s.person_id != person_id:
        raise HTTPException(status_code=404, detail="报告批次不存在")
    db.delete(s)
    db.commit()
    return None
