
from typing import Optional
from pydantic import BaseModel, Field

class ProductBrandBase(BaseModel):
    """
    Base schema for a Product Brand.
    """
    name: str = Field(default=None, description="The name of the product brand")
    description: Optional[str] = Field(default=None, description="The description of the product brand")

# Modelo para crear una nueva tarea (hereda de TaskBase)
class ProductBrandCreate(ProductBrandBase):
    """
    Schema for creating a Product Brand.
    """
    pass

class ProductBrandUpdate(ProductBrandBase):
    """
    Schema for updating a Product Brand.
    """
    pass

class ProductBrandRead(BaseModel):
    """
    Schema for reading a Product Brand.
    """
    id: int = Field(description="The primary key")
    name: str = Field(description="The name of the product brand")
    description: Optional[str] = Field(None, description="The description of the product brand")
    model_config = {"from_attributes": True}