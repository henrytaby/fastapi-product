from typing import Optional

from sqlmodel import Field, SQLModel


class BaseModel(SQLModel):
    """
    Base model that includes common fields for all models.
    """

    id: Optional[int] = Field(
        default=None, primary_key=True, description="The primary key"
    )
