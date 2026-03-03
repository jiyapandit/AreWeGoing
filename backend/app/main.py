from fastapi import FastAPI
from db.session import engine
from sqlalchemy import text

app = FastAPI(title="AreWeGoing API", version="0.1.0")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/db-check")
def db_check():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1")).scalar()
    return {"db": "ok", "result": result}