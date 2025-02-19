
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, SQLModel

class ProductCategory(SQLModel, table=True):
    __tablename__ = "product_category"
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(default=None)
    description: str | None = Field(default=None)
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), nullable=True
        ),
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now(), nullable=True),
    )