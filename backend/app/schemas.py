from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class PersonCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    gender: Optional[str] = Field(None, max_length=16)
    birth_date: Optional[date] = None
    member_role: Optional[str] = Field(None, max_length=64, description="家庭内角色，如父亲、儿子等")
    notes: Optional[str] = None


class PersonUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    gender: Optional[str] = None
    birth_date: Optional[date] = None
    member_role: Optional[str] = Field(None, max_length=64)
    notes: Optional[str] = None


class PersonRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    gender: Optional[str]
    birth_date: Optional[date]
    member_role: Optional[str] = None
    blood_type: Optional[str] = Field(None, description="来自报告血型指标，自然年覆盖解析")
    height_cm: Optional[float] = Field(None, description="来自报告身高指标，自然年覆盖解析")
    weight_kg: Optional[float] = Field(None, description="来自报告体重指标，自然年覆盖解析")
    notes: Optional[str]
    created_at: datetime
    avatar_url: Optional[str] = Field(None, description="自定义头像路径；为空则前端使用占位缩写头像")
    current_abnormal_count: int = Field(default=0, ge=0, description="当前仍为异常的细项数量（自然年覆盖规则）")
    current_normal_indicator_count: int = Field(
        default=0,
        ge=0,
        description="当前在自然年规则下判为正常的细项数量（按有观测记录的叶子指标计）",
    )


class PersonReadList(PersonRead):
    """成员列表专用：与 PersonRead 字段一致。"""


class CurrentAbnormalItem(BaseModel):
    """某一仍为「当前异常」的细项及其判定依据观测。"""

    indicator_id: int
    indicator_name: str
    indicator_category: str
    indicator_is_narrative: bool
    indicator_parent_name: Optional[str] = None
    basis_label: str = Field(description="判定说明（本年复查 / 沿用往年等）")
    observation_id: int
    measured_at: datetime
    session_report_at: datetime
    value_text: Optional[str] = None
    ref_text: Optional[str] = None
    abnormal: Optional[bool] = None
    remarks: Optional[str] = None
    findings_text: Optional[str] = None
    conclusion_text: Optional[str] = None
    organ_names: List[str] = Field(default_factory=list)


class ExamSessionCreate(BaseModel):
    report_at: datetime
    institution: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None


class ExamSessionUpdate(BaseModel):
    report_at: Optional[datetime] = None
    institution: Optional[str] = None
    notes: Optional[str] = None


class ExamSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    person_id: int
    report_at: datetime
    institution: Optional[str]
    notes: Optional[str]
    created_at: datetime


class OrganCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    gender_scope: str = Field(
        default="all",
        pattern="^(all|male|female)$",
        description="all=全体；male=男性；female=女性",
    )
    sort_order: int = Field(default=100, ge=0, le=99999)


class OrganRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    gender_scope: str
    sort_order: int


class IndicatorCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    category: str = Field(..., pattern="^(physical|lab|imaging)$")
    parent_id: Optional[int] = None
    is_narrative: bool = False
    unit: Optional[str] = Field(None, max_length=64)
    ref_range_hint: Optional[str] = Field(None, max_length=500)
    organ_ids: List[int] = Field(default_factory=list)


class IndicatorUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[str] = Field(None, pattern="^(physical|lab|imaging)$")
    parent_id: Optional[int] = None
    is_narrative: Optional[bool] = None
    unit: Optional[str] = None
    ref_range_hint: Optional[str] = None
    organ_ids: Optional[List[int]] = None


class IndicatorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    parent_id: Optional[int]
    name: str
    category: str
    is_narrative: bool
    unit: Optional[str]
    ref_range_hint: Optional[str]
    organ_ids: List[int] = Field(default_factory=list)


class ObservationCreateItem(BaseModel):
    indicator_id: int
    measured_at: Optional[datetime] = None
    value_text: Optional[str] = Field(None, max_length=500)
    ref_text: Optional[str] = Field(None, max_length=500)
    abnormal: Optional[bool] = None
    remarks: Optional[str] = None
    findings_text: Optional[str] = None
    conclusion_text: Optional[str] = None


class ObservationUpdate(BaseModel):
    indicator_id: Optional[int] = None
    measured_at: Optional[datetime] = None
    value_text: Optional[str] = Field(None, max_length=500)
    ref_text: Optional[str] = Field(None, max_length=500)
    abnormal: Optional[bool] = None
    remarks: Optional[str] = None
    findings_text: Optional[str] = None
    conclusion_text: Optional[str] = None


class ObservationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: int
    indicator_id: int
    measured_at: datetime
    value_text: Optional[str]
    ref_text: Optional[str]
    abnormal: Optional[bool]
    remarks: Optional[str]
    findings_text: Optional[str]
    conclusion_text: Optional[str]
    indicator_name: str
    indicator_category: str
    indicator_is_narrative: bool
    indicator_parent_id: Optional[int]
    indicator_parent_name: Optional[str]
    indicator_unit: Optional[str]
    indicator_ref_range_hint: Optional[str] = None
    organ_ids: List[int]
    organ_names: List[str]
    session_report_at: datetime


class ExportFiltersBody(BaseModel):
    """CSV 导出时间筛选（POST JSON）；字段可选，均为 null/省略表示该侧不限制。"""

    measured_from: Optional[datetime] = None
    measured_to: Optional[datetime] = None
    report_from: Optional[datetime] = None
    report_to: Optional[datetime] = None


class LoginBody(BaseModel):
    username: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=1, max_length=512)


class UsernameUpdate(BaseModel):
    """修改登录账户显示名（亦即登录用户名）。"""

    username: str = Field(..., min_length=1, max_length=64)
