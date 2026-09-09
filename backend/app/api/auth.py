from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import User
from app.schemas import AuthUserResponse, LoginRequest
from app.services.auth_service import verify_password

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login", response_model=AuthUserResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate a user by username and password.
    Returns the user profile with their role (INSPECTOR or MANUFACTURER).
    Returns 401 for invalid credentials.
    """
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    return AuthUserResponse(
        id=user.id,
        username=user.username,
        role=user.role,
        full_name=user.full_name,
        organization=user.organization,
    )
