from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.auth import schemas, utils
from app.auth.service import AuthService
from app.core.db import SessionDep

router = APIRouter()
service = AuthService()


@router.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: SessionDep):
    """
    create new user

    This function will create a new user with the encrypted password
    """
    return service.create_user(user, db)


@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    db: SessionDep,
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    return service.login_for_access_token(db, form_data, request)


@router.get("/users/me/", response_model=schemas.UserResponse)
async def read_users_me(current_user: schemas.User = Depends(utils.get_current_user)):
    return current_user


@router.post("/token/refresh", response_model=schemas.Token)
async def refresh_access_token(db: SessionDep, refresh_token: str):
    return service.refresh_access_token(db, refresh_token)


@router.post("/logout", response_model=dict)
async def logout(
    db: SessionDep,
    token: str = Depends(utils.oauth2_scheme),
    logout_data: schemas.LogoutRequest | None = None,
):
    refresh_token = logout_data.refresh_token if logout_data else None
    service.logout(db, token, refresh_token)
    return {"msg": "Successfully logged out"}


@router.get("/me/roles", response_model=list[schemas.RoleInfo])
async def read_users_roles(
    db: SessionDep, current_user: schemas.User = Depends(utils.get_current_user)
):
    """
    Get all active roles assigned to the current user (or all if superuser).
    """
    return service.get_user_roles(current_user, db)


@router.get("/me/menu/{role_id}", response_model=list[schemas.ModuleGroupMenu])
async def read_user_menu(
    role_id: int,
    db: SessionDep,
    current_user: schemas.User = Depends(utils.get_current_user),
):
    """
    Get the menu structure for a specific role.
    """
    return service.get_role_menu(current_user, role_id, db)
