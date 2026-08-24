from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import SessionLocal
from models import User

router = APIRouter(prefix="/auth")


class AuthRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


@router.post("/register")
def register(data: RegisterRequest):
    db = SessionLocal()
    if db.query(User).filter(User.email == data.email).first():
        db.close()
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(name=data.name, email=data.email, password=data.password)
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return {"id": user.id, "name": user.name, "email": user.email}


@router.post("/login")
def login(data: AuthRequest):
    db = SessionLocal()
    user = db.query(User).filter(User.email == data.email, User.password == data.password).first()
    db.close()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"id": user.id, "name": user.name, "email": user.email}
