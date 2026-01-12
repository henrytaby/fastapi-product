from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Column, DateTime, Field, Relationship

from app.models.base_model import BaseModel
from app.util.datetime import get_current_time

if TYPE_CHECKING:
    from .role import Role


class User(BaseModel, table=True):
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    first_name: str | None = Field(default=None)
    last_name: str | None = Field(default=None)
    is_verified: bool = Field(default=False)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    password_hash: str = Field(exclude=True)

    created_at: Optional[datetime] = Field(
        default_factory=get_current_time,
        sa_column=Column(DateTime(timezone=False), nullable=True),
        description="The timestamp when the data was created",
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=False), onupdate=get_current_time, nullable=True
        ),
        description="The timestamp when the data was last updated",
    )
    # Relatoinship
    user_roles: List["UserRole"] = Relationship(back_populates="user")


class UserRole(BaseModel, table=True):
    __tablename__ = "user_role"
    is_active: bool = Field(default=True)
    created_at: Optional[datetime] = Field(
        default_factory=get_current_time,
        sa_column=Column(DateTime(timezone=False), nullable=True),
        description="The timestamp when the data was created",
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=False), onupdate=get_current_time, nullable=True
        ),
        description="The timestamp when the data was last updated",
    )

    # Relatoinship
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    user: Optional["User"] = Relationship(back_populates="user_roles")

    role_id: Optional[int] = Field(default=None, foreign_key="role.id")
    role: Optional["Role"] = Relationship(back_populates="user_roles")


class UserRevokedToken(BaseModel, table=True):
    __tablename__ = "user_revoked_token"
    token: str = Field(index=True, unique=True)
    user_id: int = Field(index=True)
    revoked_at: Optional[datetime] = Field(
        default_factory=get_current_time,
        sa_column=Column(DateTime(timezone=False), nullable=True),
        description="The timestamp when the token was Revoked",
    )


class UserLogLogin(BaseModel, table=True):
    __tablename__ = "user_log_login"
    created_at: Optional[datetime] = Field(
        default_factory=get_current_time,
        sa_column=Column(DateTime(timezone=False), nullable=True),
        description="The timestamp when the log was created",
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=False), onupdate=get_current_time, nullable=True
        ),
        description="The timestamp when the log was last updated",
    )
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    username: Optional[str] = Field(
        description="The username used in the login attempt", default=None
    )
    password: Optional[str] = Field(
        description="The password used in the login attempt", default=None
    )
    token: Optional[str] = Field(description="The generated token", default=None)
    token_expiration: Optional[datetime] = Field(
        description="The expiration date and time of the token", default=None
    )
    ip_address: str = Field(
        description="The IP address from where the user is authenticating"
    )
    host_info: str = Field(description="Host information")
    logged_out_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=False), nullable=True),
        description="The timestamp when the user logged out",
    )
    is_successful: bool = Field(
        description="Indicates if the login attempt was successful"
    )
