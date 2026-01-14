from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Column, DateTime, Field, Relationship

from app.models.base_model import BaseModel
from app.util.datetime import get_current_time

if TYPE_CHECKING:
    from .module import Module
    from .user import UserRole


class RoleModule(BaseModel, table=True):
    __tablename__ = "role_module"
    description: str | None = Field(default=None)
    is_active: bool = Field(default=True)

    can_create: bool = Field(default=False)
    # can_read: bool = Field(default=False)
    can_update: bool = Field(default=False)
    can_delete: bool = Field(default=False)

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
    role_id: Optional[int] = Field(default=None, foreign_key="role.id")
    role: Optional["Role"] = Relationship(back_populates="role_modules")

    module_id: Optional[int] = Field(default=None, foreign_key="module.id")
    module: Optional["Module"] = Relationship(back_populates="role_modules")


class Role(BaseModel, table=True):
    name: str = Field(index=True, unique=True)
    description: str | None = Field(default=None)
    is_active: bool = Field(default=True)
    icon: str | None = Field(default=None)
    sort_order: int | None = Field(default=None)

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
    role_modules: List["RoleModule"] = Relationship(back_populates="role")
    user_roles: List["UserRole"] = Relationship(back_populates="role")
