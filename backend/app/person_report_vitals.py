"""成员血型、身高、体重：按报告与自然年覆盖解析（与本年异常判定同年界思路一致）。"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional, TypedDict

from sqlalchemy.orm import Session

from app.current_abnormals import _aware_utc, calendar_year_bounds_utc
from app.models import ExamSession, Indicator, Observation, Person

VITAL_INDICATOR_NAMES = ("身高", "体重", "血型")


class ReportVitals(TypedDict):
    blood_type: Optional[str]
    height_cm: Optional[float]
    weight_kg: Optional[float]


def _obs_has_display_value(o: Observation) -> bool:
    return bool(o.value_text and str(o.value_text).strip())


def pick_vital_observation(
    observations: List[Observation],
    reference: Optional[datetime] = None,
) -> Optional[Observation]:
    """
    优先采用**当前自然年内**最新一条有 ``value_text`` 的记录；
    若本年内没有有值记录，则采用**本年之前**最新一条有值的记录。
    """
    if not observations:
        return None
    start, end = calendar_year_bounds_utc(reference)
    desc = sorted(observations, key=lambda o: (o.measured_at, o.id), reverse=True)
    for o in desc:
        if start <= _aware_utc(o.measured_at) < end and _obs_has_display_value(o):
            return o
    for o in desc:
        if _aware_utc(o.measured_at) < start and _obs_has_display_value(o):
            return o
    return None


def _parse_float_loose(raw: str) -> Optional[float]:
    s = raw.strip().replace(",", ".")
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _observation_to_vital_fields(name: str, o: Observation) -> tuple[Optional[str], Optional[float], Optional[float]]:
    raw = (o.value_text or "").strip()
    if name == "血型":
        return (raw or None, None, None)
    if name == "身高":
        h = _parse_float_loose(raw)
        return (None, h, None)
    if name == "体重":
        w = _parse_float_loose(raw)
        return (None, None, w)
    return (None, None, None)


def empty_result() -> ReportVitals:
    return {"blood_type": None, "height_cm": None, "weight_kg": None}


def resolve_report_vitals_for_person(db: Session, person_id: int, reference=None) -> ReportVitals:
    batch = resolve_report_vitals_batch(db, [person_id], reference=reference)
    return batch.get(person_id, empty_result())


def resolve_report_vitals_batch(
    db: Session,
    person_ids: List[int],
    reference: Optional[datetime] = None,
) -> Dict[int, ReportVitals]:
    if not person_ids:
        return {}

    indicators = (
        db.query(Indicator).filter(Indicator.name.in_(VITAL_INDICATOR_NAMES)).all()
    )
    name_to_ind_ids: Dict[str, List[int]] = defaultdict(list)
    for ind in indicators:
        name_to_ind_ids[ind.name].append(ind.id)
    all_ind_ids = [i.id for i in indicators]
    if not all_ind_ids:
        return {pid: empty_result() for pid in person_ids}

    obs_rows = (
        db.query(Observation)
        .join(ExamSession)
        .filter(
            ExamSession.person_id.in_(person_ids),
            Observation.indicator_id.in_(all_ind_ids),
        )
        .all()
    )

    groups: Dict[tuple[int, int], List[Observation]] = defaultdict(list)
    for o in obs_rows:
        pid = o.session.person_id
        groups[(pid, o.indicator_id)].append(o)

    out: Dict[int, ReportVitals] = {pid: empty_result() for pid in person_ids}

    for pid in person_ids:
        bt, h, w = None, None, None
        for name in VITAL_INDICATOR_NAMES:
            combined: List[Observation] = []
            for iid in name_to_ind_ids.get(name, []):
                combined.extend(groups.get((pid, iid), []))
            wit = pick_vital_observation(combined, reference=reference)
            if not wit:
                continue
            b1, h1, w1 = _observation_to_vital_fields(name, wit)
            if b1 is not None:
                bt = b1
            if h1 is not None:
                h = h1
            if w1 is not None:
                w = w1
        out[pid] = {"blood_type": bt, "height_cm": h, "weight_kg": w}

    return out


def person_read_payload(
    p: Person,
    vit: ReportVitals,
    *,
    current_abnormal_count: int = 0,
    current_normal_indicator_count: int = 0,
) -> dict:
    """构造 ``PersonRead`` 用字典：血型 / 身高 / 体重取自 ``vit``（报告解析结果）。"""
    return {
        "id": p.id,
        "name": p.name,
        "gender": p.gender,
        "birth_date": p.birth_date,
        "member_role": p.member_role,
        "blood_type": vit["blood_type"],
        "height_cm": vit["height_cm"],
        "weight_kg": vit["weight_kg"],
        "notes": p.notes,
        "created_at": p.created_at,
        "avatar_url": (
            f"/api/persons/{p.id}/avatar"
            if getattr(p, "avatar_rel_path", None)
            else None
        ),
        "current_abnormal_count": current_abnormal_count,
        "current_normal_indicator_count": current_normal_indicator_count,
    }
