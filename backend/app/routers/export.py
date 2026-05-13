from __future__ import annotations

import csv
import io
import re
from datetime import date, datetime, timezone
from typing import List, Optional
from urllib.parse import quote

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import ExamSession, Observation, Person
from app.person_report_vitals import resolve_report_vitals_for_person
from app.schemas import ExportFiltersBody
from app.deps import require_auth

router = APIRouter(prefix="/api/persons", tags=["export"], dependencies=[Depends(require_auth)])

_FS_UNSAFE = re.compile(r'[\\/:*?"<>|\x00-\x1f]')


def _today_calendar() -> date:
    """用于计算周岁的「今天」：优先东八区，与家庭场景一致。"""
    try:
        from zoneinfo import ZoneInfo

        return datetime.now(ZoneInfo("Asia/Shanghai")).date()
    except Exception:
        return date.today()


def _age_segment(birth: Optional[date]) -> str:
    if birth is None:
        return "年龄未知"
    today = _today_calendar()
    y = today.year - birth.year
    if (today.month, today.day) < (birth.month, birth.day):
        y -= 1
    return f"{y}岁" if y >= 0 else "年龄未知"


def _safe_filename_stem(raw: str, max_len: int = 72) -> str:
    """文件名主体：去掉路径非法字符，避免过长。"""
    s = _FS_UNSAFE.sub("_", (raw or "").strip()) or "未命名"
    s = re.sub(r"_+", "_", s).strip("_")
    return s[:max_len]


def _export_timestamp(now: datetime) -> str:
    return now.strftime("%Y%m%d_%H%M%S")


def _export_disposition_header(person: Person) -> str:
    """成员姓名 + 年龄 + 导出时间；附带 ASCII 回退与 UTF-8 RFC5987。"""
    try:
        from zoneinfo import ZoneInfo

        now = datetime.now(ZoneInfo("Asia/Shanghai"))
    except Exception:
        now = datetime.now()
    name_stem = _safe_filename_stem(person.name)
    age_stem = _age_segment(person.birth_date)
    ts = _export_timestamp(now)
    unicode_name = f"{name_stem}_{age_stem}_{ts}.csv"
    ascii_fallback = f"export_{person.id}_{ts}.csv"
    enc = quote(unicode_name, safe="")
    return f'attachment; filename="{ascii_fallback}"; filename*=UTF-8\'\'{enc}'


def _normalize_query_datetime(dt: Optional[datetime]) -> Optional[datetime]:
    """SQLite 存的是无时区 naive；筛选条件经 ISO 多为带时区，统一转为 UTC naive 再比较。"""
    if dt is None:
        return None
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


def _csv_rows_for_person(
    db: Session,
    person_id: int,
    time_from: Optional[datetime],
    time_to: Optional[datetime],
    report_from: Optional[datetime],
    report_to: Optional[datetime],
) -> tuple[List[List[str]], Person]:
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
    if report_from is not None:
        q = q.filter(ExamSession.report_at >= report_from)
    if report_to is not None:
        q = q.filter(ExamSession.report_at <= report_to)
    q = q.order_by(Observation.measured_at.asc(), Observation.id.asc())
    rows = q.all()

    vit = resolve_report_vitals_for_person(db, person_id)

    header = [
        "person_id",
        "person_name",
        "gender",
        "birth_date",
        "member_role",
        "blood_type",
        "measured_at",
        "session_report_at",
        "session_institution",
        "session_notes",
        "indicator_id",
        "indicator_parent",
        "indicator",
        "category",
        "indicator_unit",
        "is_narrative",
        "value",
        "ref",
        "abnormal",
        "remarks",
        "findings",
        "conclusion",
        "organs",
    ]
    lines: List[List[str]] = [header]
    for obs in rows:
        ind = obs.indicator
        parent = ind.parent
        sess = obs.session
        organ_names = ";".join(o.name for o in ind.organs)
        lines.append(
            [
                str(person.id),
                person.name,
                person.gender or "",
                person.birth_date.isoformat() if person.birth_date else "",
                person.member_role or "",
                vit["blood_type"] or "",
                obs.measured_at.isoformat(),
                sess.report_at.isoformat(),
                sess.institution or "",
                sess.notes or "",
                str(ind.id),
                parent.name if parent else "",
                ind.name,
                ind.category,
                ind.unit or "",
                "是" if ind.is_narrative else "否",
                obs.value_text or "",
                obs.ref_text or "",
                "" if obs.abnormal is None else ("是" if obs.abnormal else "否"),
                obs.remarks or "",
                obs.findings_text or "",
                obs.conclusion_text or "",
                organ_names,
            ]
        )
    return lines, person


def _make_csv_response(person: Person, lines: List[List[str]]) -> Response:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerows(lines)
    data = "\ufeff" + buf.getvalue()
    return Response(
        content=data.encode("utf-8"),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": _export_disposition_header(person),
        },
    )


@router.get("/{person_id}/export")
def export_person_observations_csv(
    person_id: int,
    time_from: Optional[datetime] = Query(
        None,
        alias="from",
        description="测量时间下限（含），ISO8601；可与 measured_from 二选一",
    ),
    time_to: Optional[datetime] = Query(
        None,
        alias="to",
        description="测量时间上限（含）；可与 measured_to 二选一",
    ),
    measured_from_q: Optional[datetime] = Query(
        None,
        alias="measured_from",
        description="测量时间下限（含），与 from 等价，避免部分代理丢弃 from 参数",
    ),
    measured_to_q: Optional[datetime] = Query(
        None,
        alias="measured_to",
        description="测量时间上限（含），与 to 等价",
    ),
    report_from: Optional[datetime] = Query(
        None,
        alias="report_from",
        description="批次报告时间下限（含），与测量时间条件 AND",
    ),
    report_to: Optional[datetime] = Query(
        None,
        alias="report_to",
        description="批次报告时间上限（含）",
    ),
    db: Session = Depends(get_db),
):
    tf = _normalize_query_datetime(time_from or measured_from_q)
    tt = _normalize_query_datetime(time_to or measured_to_q)
    rf = _normalize_query_datetime(report_from)
    rt = _normalize_query_datetime(report_to)
    lines, person = _csv_rows_for_person(db, person_id, tf, tt, rf, rt)
    return _make_csv_response(person, lines)


@router.post("/{person_id}/export")
def export_person_observations_csv_post(
    person_id: int,
    filters: ExportFiltersBody = Body(default_factory=ExportFiltersBody),
    db: Session = Depends(get_db),
):
    """带条件导出（推荐）：请求体 JSON 传参，不依赖 URL 查询串，避免 from 等参数被中间层丢弃。"""
    tf = _normalize_query_datetime(filters.measured_from)
    tt = _normalize_query_datetime(filters.measured_to)
    rf = _normalize_query_datetime(filters.report_from)
    rt = _normalize_query_datetime(filters.report_to)
    lines, person = _csv_rows_for_person(db, person_id, tf, tt, rf, rt)
    return _make_csv_response(person, lines)
