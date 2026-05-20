import secrets

from fastapi import APIRouter, HTTPException, status

from app.core.config import get_settings
from app.core.security import create_access_token
from app.schemas.auth import LoginRequest, LoginResponse


router = APIRouter(tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    settings = get_settings()
    username_ok = secrets.compare_digest(payload.username, settings.default_username)
    password_ok = secrets.compare_digest(payload.password, settings.default_password)

    if not username_ok or not password_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
        )

    user = {
        "id": "qa-admin",
        "name": "QA Administrator",
        "email": f"{settings.default_username}@local.ai",
        "role": "QA Lead",
    }
    token = create_access_token(subject=user["id"], extra_claims=user)
    return LoginResponse(token=token, user=user)
