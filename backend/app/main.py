from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from db.session import engine
from sqlalchemy import text
from app.modules.auth.router import router as auth_router
from app.modules.groups.router import router as groups_router
from app.modules.preferences.router import router as preferences_router

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
