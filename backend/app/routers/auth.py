"""Authentication API endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import bearer_scheme, get_auth_service, get_current_active_user
from app.models.models import User
from app.schemas.auth import CurrentUserOut, LoginRequest, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


def serialize_current_user(user: User, auth_service: AuthService) -> CurrentUserOut:
    return CurrentUserOut(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=auth_service.resolve_user_role(user),
        organization_id=user.organization_id,
        organization_name=user.organization.name if user.organization else None,
        is_active=user.is_active,
        last_login_at=user.last_login_at,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.post("/login", response_model=TokenResponse)
def login(
    credentials: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    user = auth_service.authenticate_user(credentials.email, credentials.password)
    access_token = auth_service.build_access_token_for_user(user)
    return TokenResponse(access_token=access_token)


@router.get(
    "/me",
    response_model=CurrentUserOut,
    dependencies=[Depends(bearer_scheme)],
)
def read_current_user(
    current_user: User = Depends(get_current_active_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    return serialize_current_user(current_user, auth_service)
