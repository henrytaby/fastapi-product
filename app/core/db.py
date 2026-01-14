import json
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings

# from ..models.module import Module, ModuleGroup
# from ..models.role import Role, RoleModule
# from ..models.user import User, UserRole, UserRevokedToken

"""
Docs about this implementation
https://fastapi.tiangolo.com/tutorial/sql-databases/#run-the-app
"""


def json_serializer(obj):
    return json.dumps(obj, ensure_ascii=False)


engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    json_serializer=json_serializer,
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
