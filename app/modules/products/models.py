from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Column, DateTime, Field, Relationship

from app.models.base_model import BaseModel
from app.util.datetime import get_current_time

if TYPE_CHECKING:
    from ..catalog.products_brand.models import ProductBrand
    from ..catalog.products_category.models import ProductCategory


class Product(BaseModel, table=True):
    """
    Product model that represents a product in the database.
    """

    __tablename__ = "product"
    title: str = Field(default=None)
    price: int = 0
    description: Optional[str] = Field(default=None)
    image: str = Field(default=None)

    category_id: Optional[int] = Field(default=None, foreign_key="product_category.id")
    category: Optional["ProductCategory"] = Relationship(back_populates="products")

    brand_id: Optional[int] = Field(default=None, foreign_key="product_brand.id")
    brand: Optional["ProductBrand"] = Relationship(back_populates="products")

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
