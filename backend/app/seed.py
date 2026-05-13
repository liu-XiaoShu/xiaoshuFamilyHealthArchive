"""Seed organs and indicators if tables are empty."""

from __future__ import annotations

from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.import_lexicon import ensure_import_lexicon
from app.models import Indicator
from app.organs_catalog import ensure_standard_organs


def seed_reference_data(db: Session) -> None:
    organs = ensure_standard_organs(db)

    if db.query(Indicator).first() is not None:
        db.commit()
        ensure_import_lexicon(db)
        return

    def link(ind: Indicator, *organ_names: str) -> None:
        for n in organ_names:
            ind.organs.append(organs[n])

    physical: List[Tuple[str, bool, Optional[str], Optional[str], Tuple[str, ...]]] = [
        ("身高", False, "cm", None, ("骨骼肌肉",)),
        ("体重", False, "kg", None, ("骨骼肌肉",)),
        ("血型", False, None, None, ("血液",)),
        ("收缩压", False, "mmHg", "90–140", ("心脏",)),
        ("舒张压", False, "mmHg", "60–90", ("心脏",)),
    ]
    for name, narrative, unit, ref_hint, ot in physical:
        ind = Indicator(
            name=name,
            category="physical",
            is_narrative=narrative,
            unit=unit,
            ref_range_hint=ref_hint,
            parent_id=None,
        )
        link(ind, *ot)
        db.add(ind)

    db.flush()

    cbc = Indicator(
        name="血常规",
        category="lab",
        is_narrative=False,
        parent_id=None,
    )
    link(cbc, "血液")
    db.add(cbc)
    db.flush()
    wbc = Indicator(
        name="白细胞",
        category="lab",
        is_narrative=False,
        unit="×10⁹/L",
        ref_range_hint="3.5–9.5",
        parent_id=cbc.id,
    )
    link(wbc, "血液")
    db.add(wbc)

    ur = Indicator(name="尿常规", category="lab", is_narrative=False, parent_id=None)
    link(ur, "肾脏")
    db.add(ur)
    db.flush()
    up = Indicator(
        name="尿蛋白",
        category="lab",
        is_narrative=False,
        unit=None,
        ref_range_hint="阴性",
        parent_id=ur.id,
    )
    link(up, "肾脏")
    db.add(up)

    liver = Indicator(
        name="肝功能检查",
        category="lab",
        is_narrative=False,
        parent_id=None,
    )
    link(liver, "肝脏")
    db.add(liver)
    db.flush()
    bili = Indicator(
        name="血清总胆红素",
        category="lab",
        is_narrative=False,
        unit="μmol/L",
        ref_range_hint="5.1–28",
        parent_id=liver.id,
    )
    link(bili, "肝脏")
    db.add(bili)

    cardiac_enzyme = Indicator(
        name="心肌酶",
        category="lab",
        is_narrative=False,
        unit="U/L",
        parent_id=None,
    )
    link(cardiac_enzyme, "心脏")
    db.add(cardiac_enzyme)

    imaging: List[Tuple[str, bool, Tuple[str, ...]]] = [
        ("心脏彩超", True, ("心脏",)),
        ("颈椎CT", True, ("骨骼肌肉",)),
        ("腰部核磁共振", True, ("骨骼肌肉",)),
    ]
    for name, narrative, ot in imaging:
        ind = Indicator(
            name=name,
            category="imaging",
            is_narrative=narrative,
            parent_id=None,
        )
        link(ind, *ot)
        db.add(ind)

    db.commit()

    ensure_import_lexicon(db)
