from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field

router = APIRouter()


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=2)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


@router.post("/register")
def register(payload: RegisterRequest) -> dict:
    return {
        "message": "User registered",
        "user": {"email": payload.email, "full_name": payload.full_name},
    }


@router.post("/login")
def login(payload: LoginRequest) -> dict:
    if "@" not in payload.email:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    expires_at = datetime.now(timezone.utc) + timedelta(hours=12)
    return {
        "access_token": f"demo-token-{payload.email}",
        "token_type": "bearer",
        "expires_at": expires_at.isoformat(),
    }
