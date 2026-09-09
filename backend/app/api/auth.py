from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from ..services.user_database import user_database


router = APIRouter(prefix="/api/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    user_id: str
    password: str


class LoginResponse(BaseModel):
    user_id: str
    name: str
    role: str
    department: Optional[str] = None
    status: str


@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest):
    user = user_database.authenticate(
        payload.user_id.strip(),
        payload.password,
    )

    if not user:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=401,
            detail="Invalid user ID or password.",
        )

    return LoginResponse(**user)