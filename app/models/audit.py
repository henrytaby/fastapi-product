from datetime import datetime
from typing import Any, Optional

from sqlalchemy import JSON, Column, DateTime
from sqlmodel import Field, SQLModel

from app.util.datetime import get_current_time


class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_log"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, index=True)
    username: Optional[str] = Field(default=None)
    action: str = Field(index=True)  # CREATE, READ, UPDATE, DELETE, ACCESS
    entity_type: str = Field(index=True)  # Product, User, Endpoint
    entity_id: Optional[str] = Field(default=None, index=True)
    changes: Optional[Any] = Field(default=None, sa_column=Column(JSON))
    ip_address: Optional[str] = Field(default=None)
    user_agent: Optional[str] = Field(default=None)
    timestamp: datetime = Field(
        default_factory=get_current_time,
        sa_column=Column(DateTime(timezone=False), index=True),
    )
