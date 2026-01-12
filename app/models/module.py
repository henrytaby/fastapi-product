from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Column, DateTime, Field, Relationship

from app.models.base_model import BaseModel
from app.util.datetime import get_current_time

if TYPE_CHECKING:
    from .role import RoleModule


class ModuleGroup(BaseModel, table=True):
    __tablename__ = "module_group"
    name: str = Field(index=True, unique=True)
    description: str | None = Field(default=None)
    order: int | None = Field(default=None)
    icon: str | None = Field(default=None)
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
    modules: List["Module"] = Relationship(back_populates="group")


class Module(BaseModel, table=True):
    name: str = Field(index=True, unique=True)
    description: str | None = Field(default=None)
    can_create: bool = Field(default=False)
    # can_read: bool = Field(default=False)
    can_update: bool = Field(default=False)
    can_delete: bool = Field(default=False)
    is_active: bool = Field(default=True)
    icon: str | None = Field(default=None)
    route: str | None = Field(default=None)
    order: int | None = Field(default=None)

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
    group_id: Optional[int] = Field(default=None, foreign_key="module_group.id")
    group: Optional["ModuleGroup"] = Relationship(back_populates="modules")

    role_modules: List["RoleModule"] = Relationship(back_populates="module")
