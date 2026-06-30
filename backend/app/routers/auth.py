"""Authentication API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import User
from app.dependencies.auth import get_current_active_user
from app.schemas.auth import CurrentUserOut, LoginRequest, TokenResponse
from app.services.auth_service import (
    InactiveUserError,
    InvalidCredentialsError,
    authenticate_user,
    build_access_token_for_user,
    resolve_user_role,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


def serialize_current_user(user: User) -> CurrentUserOut:
    return CurrentUserOut(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=resolve_user_role(user),
        organization_id=user.organization_id,
        organization_name=user.organization.name if user.organization else None,
        is_active=user.is_active,
        last_login_at=user.last_login_at,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    try:
        user = authenticate_user(db, credentials.email, credentials.password)
        access_token = build_access_token_for_user(user)
        return TokenResponse(access_token=access_token)
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except InactiveUserError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@router.get("/me", response_model=CurrentUserOut)
def read_current_user(current_user: User = Depends(get_current_active_user)):
    return serialize_current_user(current_user)
