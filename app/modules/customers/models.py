from datetime import datetime
from typing import Optional

from pydantic import EmailStr
from sqlmodel import Column, DateTime, Field

from app.models.base_model import BaseModel
from app.util.datetime import get_current_time


class Customer(BaseModel, table=True):
    name: str = Field(default=None)
    last_name: str | None = Field(default=None)
    description: str | None = Field(default=None)
    email: EmailStr = Field(default=None)
    age: int = Field(default=None)

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
