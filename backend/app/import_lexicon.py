"""补齐 CSV 导入常用体检项目名称（启动时按需插入，不删不改已有指标）。"""

from __future__ import annotations

from typing import Iterable, Optional, Tuple

from sqlalchemy.orm import Session

from app.models import Indicator, Organ


# (分组名, 大类, 关联器官名称…)
_PANEL_PARENTS: Tuple[Tuple[str, str, Tuple[str, ...]], ...] = (
    ("生化检验", "lab", ("血液",)),
    ("肿瘤标志物", "lab", ("血液",)),
    ("幽门螺杆菌检查", "lab", ("胃",)),
)

# (细项名称, 大类, 上级分组名或空表示顶层, 是否叙述类, 关联器官…)
_PANEL_LEAVES: Tuple[Tuple[str, str, str, bool, Tuple[str, ...]], ...] = (
    ("血清尿酸", "lab", "生化检验", False, ("肾脏",)),
    ("总胆固醇", "lab", "生化检验", False, ("血液",)),
    ("低密度脂蛋白胆固醇", "lab", "生化检验", False, ("血液",)),
    ("中性粒细胞百分比", "lab", "血常规", False, ("血液",)),
    ("淋巴细胞百分比", "lab", "血常规", False, ("血液",)),
    ("嗜酸性粒细胞百分比", "lab", "血常规", False, ("血液",)),
    ("嗜碱性粒细胞百分比", "lab", "血常规", False, ("血液",)),
    ("甲胎蛋白(AFP)", "lab", "肿瘤标志物", False, ("肝脏",)),
    ("癌胚抗原(CEA)", "lab", "肿瘤标志物", False, ("血液",)),
    ("糖类抗原19-9(CA19-9)", "lab", "肿瘤标志物", False, ("胰腺",)),
    ("C13呼气试验", "lab", "幽门螺杆菌检查", False, ("胃",)),
    ("静态心电图", "imaging", "", True, ("心脏",)),
    ("腹部超声", "imaging", "", True, ("肝脏",)),
    ("甲状腺超声", "imaging", "", True, ("甲状腺",)),
    ("颈椎DR", "imaging", "", True, ("骨骼肌肉",)),
    ("肺部CT", "imaging", "", True, ("肺",)),
)


def _attach_organs(ind: Indicator, organs_map: dict[str, Organ], names: Iterable[str]) -> None:
    for n in names:
        o = organs_map.get(n)
        if o is None:
            continue
        if o not in ind.organs:
            ind.organs.append(o)


def ensure_import_lexicon(db: Session) -> None:
    """插入缺失的常见体检叶子指标（名称与主流 CSV / 瑞慈类报表对齐）。"""
    organs_map = {o.name: o for o in db.query(Organ).all()}

    for pname, pcat, org_names in _PANEL_PARENTS:
        if db.query(Indicator.id).filter(Indicator.name == pname).first():
            continue
        p = Indicator(name=pname, category=pcat, is_narrative=False, parent_id=None)
        _attach_organs(p, organs_map, org_names)
        db.add(p)

    db.flush()

    for name, cat, parent_name, narrative, org_names in _PANEL_LEAVES:
        if db.query(Indicator.id).filter(Indicator.name == name).first():
            continue
        pid: Optional[int] = None
        if parent_name:
            row = db.query(Indicator).filter(Indicator.name == parent_name).first()
            if row is None:
                continue
            pid = row.id
        leaf = Indicator(
            name=name,
            category=cat,
            is_narrative=narrative,
            parent_id=pid,
        )
        _attach_organs(leaf, organs_map, org_names)
        db.add(leaf)

    db.commit()
