from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from database import SessionLocal
from models import User
from security import hash_password, verify_password

router = APIRouter(prefix="/auth")


class AuthRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str = Field(min_length=8)


@router.post("/register")
def register(data: RegisterRequest):
    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == data.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")
        user = User(
            name=data.name,
            email=data.email,
            password_hash=hash_password(data.password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return {"id": user.id, "name": user.name, "email": user.email}
    finally:
        db.close()


@router.post("/login")
def login(data: AuthRequest):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == data.email).first()
        if not user or not verify_password(data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return {"id": user.id, "name": user.name, "email": user.email}
    finally:
        db.close()
