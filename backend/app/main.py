from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from db.base import Base
from db.session import engine
from sqlalchemy import text
from app.modules.auth.router import router as auth_router
from app.modules.groups.router import router as groups_router
from app.modules.preferences.router import router as preferences_router
from app.modules.catalog.router import router as catalog_router
from app.modules.itinerary.router import router as itinerary_router
from app.modules.notifications.router import router as notifications_router
from app.modules.catalog.service import seed_catalog_if_empty
from db.models import User, Group, Membership, Preference, CatalogItem, Itinerary, ItineraryDay, ItineraryItem, Vote, Notification, Invite

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
    Base.metadata.create_all(bind=engine)
    db = Session(engine)
    try:
        seed_catalog_if_empty(db)
    finally:
        db.close()


@app.exception_handler(HTTPException)
async def http_exception_handler(_, exc: HTTPException):
    code = f"HTTP_{exc.status_code}"
    details = exc.detail if isinstance(exc.detail, (dict, list)) else None
    message = exc.detail if isinstance(exc.detail, str) else "Request failed"
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


@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/db-check")
def db_check():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1")).scalar()
    return {"db": "ok", "result": result}
