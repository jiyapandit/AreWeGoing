from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from db.session import engine
from app.modules.auth.router import router as auth_router
from app.modules.groups.router import router as groups_router
from app.modules.preferences.router import router as preferences_router
from app.modules.catalog.router import router as catalog_router
from app.modules.itinerary.router import router as itinerary_router
from app.modules.notifications.router import router as notifications_router
from app.modules.catalog.service import seed_catalog_if_empty

app = FastAPI(title="AreWeGoing API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(groups_router, prefix="/api/v1/groups", tags=["Groups"])
app.include_router(preferences_router)
app.include_router(itinerary_router)
app.include_router(catalog_router)
app.include_router(notifications_router)


@app.on_event("startup")
def startup():
    # Runtime schema creation is intentionally disabled.
    # Database schema must be managed through Alembic migrations.
    db = Session(engine)
    try:
        if inspect(engine).has_table("catalog_items"):
            seed_catalog_if_empty(db)
    finally:
        db.close()


@app.exception_handler(HTTPException)
async def http_exception_handler(_, exc: HTTPException):
    code = f"HTTP_{exc.status_code}"
    message = "Request failed"
    details = None

    if isinstance(exc.detail, str):
        message = exc.detail
    elif isinstance(exc.detail, list):
        details = exc.detail
    elif isinstance(exc.detail, dict):
        code = str(exc.detail.get("errorCode") or code)
        message = str(exc.detail.get("message") or message)
        details = exc.detail.get("details")

    return JSONResponse(
        status_code=exc.status_code,
        content={"errorCode": code, "message": message, "details": details},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "errorCode": "VALIDATION_ERROR",
            "message": "Invalid request payload",
            "details": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_, __):
    return JSONResponse(
        status_code=500,
        content={
            "errorCode": "HTTP_500",
            "message": "Internal server error",
            "details": None,
        },
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    checks = {"database": "fail", "schema": "fail"}
    details = {}
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except SQLAlchemyError:
        details["database"] = "Could not connect to database"

    try:
        inspector = inspect(engine)
        required_tables = ["users", "groups", "memberships", "preferences", "catalog_items"]
        missing_tables = [table for table in required_tables if not inspector.has_table(table)]
        if missing_tables:
            details["schema"] = {"missing_tables": missing_tables}
        else:
            checks["schema"] = "ok"
    except SQLAlchemyError:
        details["schema"] = "Could not inspect schema"

    is_ready = checks["database"] == "ok" and checks["schema"] == "ok"
    if not is_ready:
        return JSONResponse(status_code=503, content={"status": "not_ready", "checks": checks, "details": details})
    return {"status": "ready", "checks": checks}


@app.get("/db-check")
def db_check():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1")).scalar()
    return {"db": "ok", "result": result}
