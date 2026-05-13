from pathlib import Path
import os

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
_test_url = os.environ.get("FH_TEST_DATABASE_URL") or ""
if _test_url.strip():
    DATABASE_URL = _test_url.strip()
else:
    DATABASE_URL = f"sqlite:///{DATA_DIR / 'family_health.db'}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def migrate_sqlite_schema() -> None:
    """SQLite 无 Alembic 时补齐新增列。"""
    insp = inspect(engine)
    if "indicators" not in insp.get_table_names():
        return
    cols = {c["name"] for c in insp.get_columns("indicators")}
    if "parent_id" not in cols:
        with engine.begin() as conn:
            conn.execute(
                text(
                    "ALTER TABLE indicators ADD COLUMN parent_id INTEGER "
                    "REFERENCES indicators(id) ON DELETE SET NULL"
                )
            )

    if "organs" in insp.get_table_names():
        organ_cols = {c["name"] for c in insp.get_columns("organs")}
        if "gender_scope" not in organ_cols:
            with engine.begin() as conn:
                conn.execute(
                    text(
                        "ALTER TABLE organs ADD COLUMN gender_scope VARCHAR(16) "
                        "NOT NULL DEFAULT 'all'"
                    )
                )
        if "sort_order" not in organ_cols:
            with engine.begin() as conn:
                conn.execute(
                    text(
                        "ALTER TABLE organs ADD COLUMN sort_order INTEGER NOT NULL DEFAULT 100"
                    )
                )

    if "persons" in insp.get_table_names():
        person_cols = {c["name"] for c in insp.get_columns("persons")}
        if "member_role" not in person_cols:
            with engine.begin() as conn:
                conn.execute(
                    text("ALTER TABLE persons ADD COLUMN member_role VARCHAR(64)")
                )
        if "avatar_rel_path" not in person_cols:
            with engine.begin() as conn:
                conn.execute(
                    text("ALTER TABLE persons ADD COLUMN avatar_rel_path VARCHAR(512)")
                )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
