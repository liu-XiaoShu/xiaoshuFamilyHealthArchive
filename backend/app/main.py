from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request

from app.auth_bootstrap import bootstrap_auth_user
from app.db import Base, SessionLocal, engine, migrate_sqlite_schema
from app.routers import auth, export, import_observations, indicators, observations, persons, sessions
from app.seed import seed_reference_data
from app.settings import get_settings


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    migrate_sqlite_schema()
    db = SessionLocal()
    try:
        seed_reference_data(db)
        bootstrap_auth_user(db, get_settings())
    finally:
        db.close()
    yield


app = FastAPI(title="家庭健康管理 API", lifespan=lifespan, redirect_slashes=False)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    SessionMiddleware,
    secret_key=get_settings().fh_session_secret,
    session_cookie="fh_session",
    same_site="lax",
    https_only=False,
)


@app.middleware("http")
async def no_store_api_responses(request: Request, call_next):
    """避免浏览器或代理缓存动态 JSON（否则导入后刷新成员详情仍显示旧的当前异常计数等）。"""
    response = await call_next(request)
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store, max-age=0"
        response.headers["Pragma"] = "no-cache"
    return response


app.include_router(auth.router)
app.include_router(persons.router, prefix="/api/persons", tags=["persons"])
app.include_router(sessions.router, prefix="/api/persons/{person_id}/sessions", tags=["sessions"])
app.include_router(indicators.router, prefix="/api/indicators", tags=["indicators"])
app.include_router(observations.router, prefix="/api/persons", tags=["observations"])
app.include_router(observations.batch_router)
app.include_router(export.router)
app.include_router(import_observations.router, prefix="/api/persons", tags=["import"])


@app.get("/api/health")
def health():
    return {"status": "ok"}


_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if _dist.is_dir():
    app.mount("/", StaticFiles(directory=str(_dist), html=True), name="frontend")
