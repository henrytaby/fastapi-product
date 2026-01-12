from typing import Optional

from pydantic import BaseModel, Field


class ProductCategoryBase(BaseModel):
    """
    Base schema for a product category.
    """

    name: str | None = Field(
        default=None, description="The name of the product category"
    )
    description: Optional[str] = Field(
        default=None, description="The description of the product category"
    )


# Modelo para crear una nueva tarea (hereda de TaskBase)
class ProductCategoryCreate(ProductCategoryBase):
    """
    Schema for creating a new product category.
    """

    pass


class ProductCategoryUpdate(ProductCategoryBase):
    """
    Schema for updating an existing product category.
    """

    pass


class ProductCategoryRead(BaseModel):
    """
    Schema for reading a product category.
    """

    id: int = Field(description="The primary key")
    name: str = Field(description="The name of the product category")
    description: Optional[str] = Field(
        None, description="The description of the product category"
    )
    model_config = {"from_attributes": True}
