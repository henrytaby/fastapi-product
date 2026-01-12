from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from sqlmodel import Session, create_engine

from app.core.config import settings

# from ..models.module import Module, ModuleGroup
# from ..models.role import Role, RoleModule
# from ..models.user import User, UserRole, UserRevokedToken

"""
Docs about this implementation
https://fastapi.tiangolo.com/tutorial/sql-databases/#run-the-app
"""
engine = create_engine(settings.DATABASE_URL, echo=False)


@asynccontextmanager
async def create_db_and_tables(app: FastAPI):
    # SQLModel.metadata.create_all(engine)
    # print(f"--[>] Server is starting ...")
    yield
    # print(f"--[x] Server has been stopped")


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
