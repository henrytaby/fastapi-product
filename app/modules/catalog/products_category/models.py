from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Column, DateTime, Field, Relationship

from app.models.base_model import BaseModel
from app.util.datetime import get_current_time

if TYPE_CHECKING:
    from app.modules.products.models import Product


class ProductCategory(BaseModel, table=True):
    """
    ProductCategory model that represents a product category in the database.
    """

    __tablename__ = "product_category"

    name: str = Field(default=None, description="The name of the product category")
    description: Optional[str] = Field(
        default=None, description="The description of the product category"
    )

    products: List["Product"] = Relationship(back_populates="category")

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
