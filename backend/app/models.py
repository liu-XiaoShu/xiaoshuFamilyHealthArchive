from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, String, Table, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class AppUser(Base):
    """简单单用户 / 管理员登录（局域网场景）。"""

    __tablename__ = "app_users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(128))


indicator_organs = Table(
    "indicator_organs",
    Base.metadata,
    Column("indicator_id", Integer, ForeignKey("indicators.id", ondelete="CASCADE"), primary_key=True),
    Column("organ_id", Integer, ForeignKey("organs.id", ondelete="CASCADE"), primary_key=True),
)


class Organ(Base):
    __tablename__ = "organs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    """适用范围：全体成员 / 男性 / 女性（生殖系统等相关条目）。"""
    gender_scope: Mapped[str] = mapped_column(String(16), default="all", index=True)
    """同类器官展示顺序（越小越靠前）。"""
    sort_order: Mapped[int] = mapped_column(Integer, default=100)

    indicators: Mapped[List["Indicator"]] = relationship(
        secondary=indicator_organs,
        back_populates="organs",
    )


class Indicator(Base):
    __tablename__ = "indicators"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("indicators.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(200), index=True)
    category: Mapped[str] = mapped_column(String(32), index=True)
    """physical | lab | imaging"""
    is_narrative: Mapped[bool] = mapped_column(Boolean, default=False)
    unit: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    ref_range_hint: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    parent: Mapped[Optional["Indicator"]] = relationship(
        back_populates="children",
        remote_side=[id],
        foreign_keys=[parent_id],
    )
    children: Mapped[List["Indicator"]] = relationship(
        back_populates="parent",
        foreign_keys=[parent_id],
    )

    organs: Mapped[List[Organ]] = relationship(
        secondary=indicator_organs,
        back_populates="indicators",
    )
    observations: Mapped[List["Observation"]] = relationship(back_populates="indicator")


class Person(Base):
    __tablename__ = "persons"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    gender: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    birth_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    """家庭内角色，如父亲、儿子、女儿等（自由文本）。"""
    member_role: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    blood_type: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    height_cm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    weight_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    """相对数据目录的头像路径，如 ``avatars/12/uuid.jpg``。"""
    avatar_rel_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    sessions: Mapped[List["ExamSession"]] = relationship(
        back_populates="person",
        cascade="all, delete-orphan",
    )


class ExamSession(Base):
    __tablename__ = "exam_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    person_id: Mapped[int] = mapped_column(ForeignKey("persons.id", ondelete="CASCADE"), index=True)
    report_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    institution: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    person: Mapped[Person] = relationship(back_populates="sessions")
    observations: Mapped[List["Observation"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )


class Observation(Base):
    __tablename__ = "observations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("exam_sessions.id", ondelete="CASCADE"), index=True)
    indicator_id: Mapped[int] = mapped_column(ForeignKey("indicators.id", ondelete="RESTRICT"), index=True)
    measured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    value_text: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    ref_text: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    abnormal: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    findings_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    conclusion_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    session: Mapped[ExamSession] = relationship(back_populates="observations")
    indicator: Mapped[Indicator] = relationship(back_populates="observations")
