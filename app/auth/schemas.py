from typing import List, Optional

from sqlmodel import Field, SQLModel


class UserCreate(SQLModel):
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    first_name: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)
    password: str
    model_config = {"extra": "forbid"}


class User(SQLModel):
    id: int
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    first_name: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)
    is_verified: bool = Field(default=False)
    password_hash: str
    model_config = {"extra": "forbid"}


class UserResponse(SQLModel):
    id: int
    username: str
    email: str
    first_name: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)
    is_verified: bool = Field(default=False)
    model_config = {"extra": "forbid"}


class Token(SQLModel):
    access_token: str
    token_type: str
    refresh_token: str


class TokenData(SQLModel):
    username: Optional[str] = None


class LogoutRequest(SQLModel):
    refresh_token: str


# --- RBAC SCHEMAS ---

class RoleInfo(SQLModel):
    id: int
    name: str
    icon: Optional[str] = None


class UserModulePermission(SQLModel):
    module_slug: str
    can_create: bool = False
    can_update: bool = False
    can_delete: bool = False
    can_read: bool = False  # Derived/Implicit permission


class ModuleMenu(SQLModel):
    name: str
    slug: str
    route: Optional[str] = None
    icon: Optional[str] = None
    sort_order: Optional[int] = None
    permissions: UserModulePermission


class ModuleGroupMenu(SQLModel):
    group_name: str
    slug: str
    icon: Optional[str] = None
    sort_order: Optional[int] = None
    modules: List[ModuleMenu]
