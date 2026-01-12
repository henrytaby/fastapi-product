from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlmodel import Session, select

from app.core.db import engine

from .models import Customer


class CustomerBase(BaseModel):
    name: str | None = Field(default=None)
    last_name: str | None = Field(default=None)
    description: str | None = Field(default=None)
    email: EmailStr | None = Field(default=None)
    age: int | None = Field(default=None)


# Modelo para crear una nueva tarea (hereda de TaskBase)
class CustomerCreate(CustomerBase):
    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        session = Session(engine)
        query = select(Customer).where(Customer.email == value)
        result = session.exec(query).first()
        if result:
            raise ValueError("This email is already registered")
        return value


class CustomerUpdate(CustomerBase):
    pass
