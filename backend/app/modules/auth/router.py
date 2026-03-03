from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.deps import get_db
from app.modules.auth.schemas import RegisterRequest, LoginRequest, AuthResponse
from app.modules.auth.service import register_user, login_user

from app.core.auth import get_current_user
from db.models.user import User

router = APIRouter()

@router.post("/register", response_model=dict, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    try:
        user = register_user(db, payload.email, payload.password)
        return {"id": user.id, "email": user.email}
    except ValueError as e:
        if str(e) == "EMAIL_ALREADY_EXISTS":
            raise HTTPException(status_code=409, detail="Email already exists")
        raise

@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    try:
        token = login_user(db, payload.email, payload.password)
        return AuthResponse(access_token=token)
    except ValueError as e:
        if str(e) == "INVALID_CREDENTIALS":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        raise

@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email}