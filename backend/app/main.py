from fastapi import FastAPI
from db.session import engine
from sqlalchemy import text
from app.modules.auth.router import router as auth_router
from app.modules.groups.router import router as groups_router
from app.modules.preferences.router import router as preferences_router

app = FastAPI(title="AreWeGoing API", version="0.1.0")
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(groups_router, prefix="/api/v1/groups", tags=["Groups"])
app.include_router(preferences_router)
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/db-check")
def db_check():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1")).scalar()
    return {"db": "ok", "result": result}