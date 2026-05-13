"""标准器官目录：补齐常用人体器官，并按性别区分生殖系统相关条目。"""

from __future__ import annotations

from typing import Literal, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models import Organ, Person

GenderNorm = Optional[Literal["male", "female"]]

# (名称, gender_scope: all | male | female, 排序序号从小到大)
STANDARD_ORGANS: list[tuple[str, str, int]] = [
    # 神经系统与感官
    ("脑", "all", 10),
    ("眼", "all", 20),
    ("耳", "all", 30),
    ("鼻", "all", 40),
    ("咽喉", "all", 50),
    # 内分泌
    ("甲状腺", "all", 60),
    ("甲状旁腺", "all", 70),
    ("肾上腺", "all", 80),
    # 循环
    ("心脏", "all", 90),
    ("血管", "all", 100),
    # 呼吸
    ("气管与支气管", "all", 110),
    ("肺", "all", 120),
    # 消化
    ("食管", "all", 130),
    ("胃", "all", 140),
    ("小肠", "all", 150),
    ("大肠", "all", 160),
    ("肝脏", "all", 170),
    ("胆囊", "all", 180),
    ("胰腺", "all", 190),
    ("脾脏", "all", 200),
    # 泌尿
    ("肾脏", "all", 210),
    ("输尿管", "all", 220),
    ("膀胱", "all", 230),
    # 血液与免疫
    ("血液", "all", 240),
    ("骨髓", "all", 250),
    ("免疫系统", "all", 260),
    # 运动与体表
    ("骨骼肌肉", "all", 270),
    ("皮肤", "all", 280),
    ("乳房", "all", 290),
    # 生殖系统（按性别）
    ("前列腺", "male", 300),
    ("睾丸附睾", "male", 310),
    ("子宫", "female", 320),
    ("卵巢", "female", 330),
    ("输卵管", "female", 340),
    ("阴道", "female", 350),
    ("宫颈", "female", 360),
    # 兜底
    ("其他", "all", 9990),
]


def normalize_person_gender(raw: Optional[str]) -> GenderNorm:
    if raw is None:
        return None
    s = str(raw).strip().lower()
    if s in ("男", "m", "male", "男性", "1"):
        return "male"
    if s in ("女", "f", "female", "女性", "2"):
        return "female"
    return None


def organs_query_filtered_for_person(db: Session, person: Person):
    """成员性别已知时排除不适用器官；未知则返回全部。"""
    q = db.query(Organ).order_by(Organ.sort_order.asc(), Organ.id.asc())
    sex = normalize_person_gender(person.gender)
    if sex is None:
        return q
    return q.filter(or_(Organ.gender_scope == "all", Organ.gender_scope == sex))


def ensure_standard_organs(db: Session) -> dict[str, Organ]:
    """插入或更新标准器官（按名称唯一），返回名称 → 模型实例。"""
    out: dict[str, Organ] = {}
    for name, scope, sort_order in STANDARD_ORGANS:
        row = db.query(Organ).filter(Organ.name == name).first()
        if row:
            if row.gender_scope != scope:
                row.gender_scope = scope
            if row.sort_order != sort_order:
                row.sort_order = sort_order
        else:
            row = Organ(name=name, gender_scope=scope, sort_order=sort_order)
            db.add(row)
        out[name] = row
    db.flush()
    return out
