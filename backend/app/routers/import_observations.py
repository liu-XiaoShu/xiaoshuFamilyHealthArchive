"""按成员批量导入观测记录（CSV）。"""

from __future__ import annotations

import csv
import io
from datetime import datetime, timezone
from typing import Optional

from dateutil import parser as date_parser
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import RedirectResponse, Response
from sqlalchemy.orm import Session

from app.deps import require_auth
from app.db import get_db
from app.models import ExamSession, Indicator, Observation, Person

router = APIRouter(dependencies=[Depends(require_auth)])

HEADER_ALIASES: dict[str, tuple[str, ...]] = {
    "report_at": ("report_at", "session_report_at", "报告时间", "批次时间"),
    # 批次（ExamSession）：同一 report_at 的多行共用；列可为空，以首条非空为准写入批次
    "institution": ("institution", "机构", "医院", "体检机构", "检查机构"),
    "session_notes": (
        "session_notes",
        "批次备注",
        "报告备注",
        "batch_notes",
        "session_remarks",
    ),
    "measured_at": ("measured_at", "测量时间"),
    "indicator_id": ("indicator_id", "指标id", "指标ID"),
    "indicator_name": (
        "indicator_name",
        "indicator",
        "指标名称",
        "检查项目",
        "细项名称",
        "指标",
    ),
    "indicator_category": (
        "indicator_category",
        "category",
        "大类",
        "类别",
        "类型",
    ),
    "value_text": ("value_text", "value", "报告值", "结果值"),
    "ref_text": ("ref_text", "ref", "标准值", "参考值", "参考范围"),
    "abnormal": ("abnormal", "是否异常", "异常"),
    "remarks": ("remarks", "备注", "说明"),
    "findings_text": ("findings_text", "findings", "报告显示", "报告描述"),
    "conclusion_text": ("conclusion_text", "conclusion", "报告结论", "结论"),
}


def _alias_lookup() -> dict[str, str]:
    rev: dict[str, str] = {}
    for canon, aliases in HEADER_ALIASES.items():
        for a in aliases:
            rev[a.strip().lower()] = canon
    return rev


_ALIAS_REV = _alias_lookup()


def _header_to_canonical(raw: str | None) -> Optional[str]:
    if raw is None:
        return None
    key = raw.strip().strip("\ufeff").strip()
    return _ALIAS_REV.get(key.lower())


def _build_header_map(fieldnames: list[str | None]) -> dict[str, str]:
    m: dict[str, str] = {}
    for fn in fieldnames:
        if not fn:
            continue
        c = _header_to_canonical(fn)
        if c:
            m[fn] = c
    return m


def _row_canonical(row: dict[str, Optional[str]], header_map: dict[str, str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw_k, val in row.items():
        c = header_map.get(raw_k)
        if not c or val is None:
            continue
        s = str(val).strip()
        if s:
            out[c] = s
    return out


def _decode_csv_bytes(raw_bytes: bytes) -> str:
    """优先 UTF-8（含 BOM）；失败则尝试简体中文 Excel 常用的 GB18030。"""
    for enc in ("utf-8-sig", "utf-8"):
        try:
            return raw_bytes.decode(enc)
        except UnicodeDecodeError:
            continue
    try:
        return raw_bytes.decode("gb18030")
    except UnicodeDecodeError as e:
        raise HTTPException(
            status_code=400,
            detail=f"无法解码 CSV（请另存为 UTF-8，或在简体 Windows Excel 下导出）：{e}",
        ) from e


def _parse_datetime(s: str) -> datetime:
    dt = date_parser.parse(s.strip(), dayfirst=False, yearfirst=True)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _parse_abnormal(s: Optional[str]) -> Optional[bool]:
    if s is None or str(s).strip() == "":
        return None
    t = str(s).strip().lower()
    if t in ("是", "y", "yes", "true", "1", "异常"):
        return True
    if t in ("否", "n", "no", "false", "0", "正常"):
        return False
    return None


def _is_leaf(db: Session, ind: Indicator) -> bool:
    return (
        db.query(Indicator.id).filter(Indicator.parent_id == ind.id).first() is None
    )


_ALLOWED_INDICATOR_CATEGORY = frozenset({"physical", "lab", "imaging"})

# 报表里常见别名 → 系统中已有指标名称
_INDICATOR_NAME_ALIASES: dict[str, str] = {
    "abo血型": "血型",
    "abo": "血型",
}


def _canonical_indicator_name(raw: str) -> str:
    s = raw.strip()
    key_compact = "".join(s.split()).casefold()
    if key_compact in _INDICATOR_NAME_ALIASES:
        return _INDICATOR_NAME_ALIASES[key_compact]
    return s


def _normalize_category(category: Optional[str]) -> Optional[str]:
    if not category:
        return None
    c = category.strip()
    zh = {
        "体格": "physical",
        "基础体格": "physical",
        "检验": "lab",
        "化验": "lab",
        "影像": "imaging",
        "影像检查": "imaging",
    }
    if c in zh:
        return zh[c]
    low = c.lower().strip()
    en_syn = {
        "ecg": "imaging",
        "ultrasound": "imaging",
        "彩超": "imaging",
        "超声": "imaging",
        "b超": "imaging",
        "心电图": "imaging",
        "dr": "imaging",
        "ct": "imaging",
    }
    if low in en_syn:
        return en_syn[low]
    return low


def _find_leaf_by_name(
    db: Session, name: str, category: Optional[str]
) -> Indicator:
    name = _canonical_indicator_name(name)
    q = db.query(Indicator).filter(Indicator.name == name)
    candidates = [i for i in q.all() if _is_leaf(db, i)]
    cat_norm = _normalize_category(category) if category else None
    if cat_norm not in _ALLOWED_INDICATOR_CATEGORY:
        cat_norm = None
    filtered = (
        [i for i in candidates if i.category == cat_norm]
        if cat_norm
        else candidates
    )
    if len(filtered) == 1:
        return filtered[0]
    # 报表大类与字典不一致（如血型标成 lab）但名称全局唯一 → 仍导入
    if len(filtered) == 0 and len(candidates) == 1:
        return candidates[0]
    if len(candidates) == 0:
        raise ValueError(f"未找到叶子指标「{name}」，请核对名称或在指标编辑中先添加")
    if len(filtered) == 0:
        cats = sorted({i.category for i in candidates})
        raise ValueError(
            f"指标「{name}」在字典中为 {cats}，与 CSV 中的 indicator_category 无法对应，请改正大类或拆分同名指标",
        )
    raise ValueError(
        f"指标名称「{name}」对应多条叶子记录，请在列 indicator_category 填写 "
        f"physical / lab / imaging（或：体格 / 检验 / 影像）以区分",
    )


def _get_or_create_session(
    db: Session, person_id: int, report_at: datetime
) -> ExamSession:
    s = (
        db.query(ExamSession)
        .filter(
            ExamSession.person_id == person_id,
            ExamSession.report_at == report_at,
        )
        .first()
    )
    if s:
        return s
    s = ExamSession(person_id=person_id, report_at=report_at)
    db.add(s)
    db.flush()
    return s


def _merge_session_batch_fields(session: ExamSession, canon: dict[str, str]) -> None:
    """写入批次级机构、备注；批次已有值则保留（首条非空优先）。"""
    inst = canon.get("institution")
    if inst and not (session.institution or "").strip():
        session.institution = inst.strip()
    sn = canon.get("session_notes")
    if sn and not (session.notes or "").strip():
        session.notes = sn.strip()


TEMPLATE_CSV = (
    "\ufeff"
    "report_at,institution,session_notes,indicator_id,indicator_name,indicator_category,"
    "value_text,ref_text,abnormal,remarks,findings_text,conclusion_text,measured_at\r\n"
    "2026-05-12T10:00:00,市人民医院,年度统筹,,身高,physical,170,,否,,,,\r\n"
    ",,,,白细胞,lab,8.2,3.5-9.5,否,,,,\r\n"
    ",,,,心脏彩超,imaging,,,是,,心影略大,建议复查\r\n"
)


@router.get("/{person_id}/import/observations-csv/template")
def download_import_template(person_id: int, db: Session = Depends(get_db)):
    if not db.get(Person, person_id):
        raise HTTPException(status_code=404, detail="成员不存在")
    return Response(
        content=TEMPLATE_CSV.encode("utf-8"),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": (
                f'attachment; filename="person_{person_id}_import_template.csv"'
            )
        },
    )


@router.post("/{person_id}/import/observations-csv")
@router.post("/{person_id}/import/observations-csv/")
async def import_observations_csv(
    person_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not db.get(Person, person_id):
        raise HTTPException(status_code=404, detail="成员不存在")
    raw_bytes = await file.read()
    if not raw_bytes:
        raise HTTPException(status_code=400, detail="文件为空")

    text = _decode_csv_bytes(raw_bytes)

    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise HTTPException(status_code=400, detail="CSV 没有表头")

    header_map = _build_header_map(list(reader.fieldnames))
    if "report_at" not in set(header_map.values()):
        raise HTTPException(
            status_code=400,
            detail="缺少必填列：report_at（或别名：报告时间、批次时间）",
        )

    imported = 0
    errors: list[dict[str, object]] = []

    prev_report_at_str: Optional[str] = None
    prev_report_at_dt: Optional[datetime] = None
    prev_institution_str: Optional[str] = None
    prev_session_notes_str: Optional[str] = None

    for lineno, raw_row in enumerate(reader, start=2):
        try:
            canon = _row_canonical(raw_row, header_map)

            if not canon.get("indicator_id") and not canon.get("indicator_name"):
                continue

            rr = canon.get("report_at")
            if rr:
                prev_report_at_str = rr
            elif prev_report_at_str:
                canon["report_at"] = prev_report_at_str
            else:
                raise ValueError(
                    "本行缺少报告时间 report_at（首行必填；其后可留空沿用上一行同一批次）",
                )

            report_at = _parse_datetime(canon["report_at"])

            if prev_report_at_dt is None or report_at != prev_report_at_dt:
                prev_institution_str = canon.get("institution")
                prev_session_notes_str = canon.get("session_notes")
            else:
                if canon.get("institution"):
                    prev_institution_str = canon["institution"]
                elif prev_institution_str:
                    canon["institution"] = prev_institution_str
                if canon.get("session_notes"):
                    prev_session_notes_str = canon["session_notes"]
                elif prev_session_notes_str:
                    canon["session_notes"] = prev_session_notes_str

            prev_report_at_dt = report_at

            id_str = canon.get("indicator_id")
            name_str = canon.get("indicator_name")
            if id_str:
                try:
                    ind_id = int(id_str)
                except ValueError as e:
                    raise ValueError("indicator_id 须为整数") from e
                ind = db.get(Indicator, ind_id)
                if not ind:
                    raise ValueError(f"指标 id 不存在：{ind_id}")
            elif name_str:
                cat_raw = canon.get("indicator_category")
                ind = _find_leaf_by_name(db, name_str, cat_raw)
                ind_id = ind.id
            else:
                raise ValueError("须提供 indicator_id 或 indicator_name")

            if not _is_leaf(db, ind):
                raise ValueError("必须使用叶子指标（细项），不能填分组节点")

            meas_raw = canon.get("measured_at")
            measured_at = _parse_datetime(meas_raw) if meas_raw else report_at

            abnormal = _parse_abnormal(canon.get("abnormal"))
            remarks = canon.get("remarks") or None

            if ind.is_narrative:
                value_text = None
                ref_text = None
                findings_text = canon.get("findings_text") or None
                conclusion_text = canon.get("conclusion_text") or None
            else:
                value_text = canon.get("value_text") or None
                ref_text = canon.get("ref_text") or None
                findings_text = None
                conclusion_text = None

            with db.begin_nested():
                session = _get_or_create_session(db, person_id, report_at)
                _merge_session_batch_fields(session, canon)
                obs = Observation(
                    session_id=session.id,
                    indicator_id=ind_id,
                    measured_at=measured_at,
                    value_text=value_text,
                    ref_text=ref_text,
                    abnormal=abnormal,
                    remarks=remarks,
                    findings_text=findings_text,
                    conclusion_text=conclusion_text,
                )
                db.add(obs)
                db.flush()
            imported += 1
        except ValueError as e:
            errors.append({"line": lineno, "detail": str(e)})
        except Exception as e:
            errors.append({"line": lineno, "detail": str(e)})

    db.commit()
    return {"imported": imported, "errors": errors}


@router.get("/{person_id}/import/observations-csv")
def observations_csv_redirect_to_template(person_id: int, db: Session = Depends(get_db)):
    """误用 GET 打开上传地址时转到模板（须注册在 POST 之后，避免 Starlette 405）。"""
    if not db.get(Person, person_id):
        raise HTTPException(status_code=404, detail="成员不存在")
    return RedirectResponse(
        url=f"/api/persons/{person_id}/import/observations-csv/template",
        status_code=307,
    )
