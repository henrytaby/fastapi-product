from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from app.auth import schemas, utils
from app.auth.service import AuthService
from app.core.db import get_session
from app.models.user import User as UserModel

router = APIRouter()


def get_auth_service(session: Session = Depends(get_session)):
    return AuthService(session)


@router.post("/users/", response_model=schemas.User)
def create_user(
    user: schemas.UserCreate, service: AuthService = Depends(get_auth_service)
):
    """
    create new user

    This function will create a new user with the encrypted password
    """
    return service.create_user(user)


@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    request: Request,
    service: AuthService = Depends(get_auth_service),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    return service.login_for_access_token(form_data, request)


@router.get("/users/me/", response_model=schemas.UserResponse)
async def read_users_me(current_user: schemas.User = Depends(utils.get_current_user)):
    return current_user


@router.post("/token/refresh", response_model=schemas.Token)
async def refresh_access_token(
    refresh_token: str, service: AuthService = Depends(get_auth_service)
):
    return service.refresh_access_token(refresh_token)


@router.post("/logout", response_model=dict)
async def logout(
    service: AuthService = Depends(get_auth_service),
    token: str = Depends(utils.oauth2_scheme),
    logout_data: schemas.LogoutRequest | None = None,
):
    refresh_token = logout_data.refresh_token if logout_data else None
    service.logout(token, refresh_token)
    return {"msg": "Successfully logged out"}


@router.get("/me/roles", response_model=list[schemas.RoleInfo])
async def read_users_roles(
    current_user: UserModel = Depends(utils.get_current_user),
    service: AuthService = Depends(get_auth_service),
):
    """
    Get all active roles assigned to the current user (or all if superuser).
    """
    return service.get_user_roles(current_user)


@router.get("/me/menu/{role_id}", response_model=list[schemas.ModuleGroupMenu])
async def read_user_menu(
    role_id: int,
    current_user: UserModel = Depends(utils.get_current_user),
    service: AuthService = Depends(get_auth_service),
):
    """
    Get the menu structure for a specific role.
    """
    return service.get_role_menu(current_user, role_id)
