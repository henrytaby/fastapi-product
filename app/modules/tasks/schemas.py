from typing import Optional

from pydantic import BaseModel, Field


class TaskBase(BaseModel):
    """
    Base schema for a task.
    """

    title: str = Field(description="The title of the task")
    description: Optional[str] = Field(None, description="The description of the task")
    completed: bool = Field(False, description="The completion status of the task")


# Modelo para crear una nueva tarea (hereda de TaskBase)
class TaskCreate(TaskBase):
    """
    Schema for creating a new task.
    """

    pass


class TaskUpdate(TaskBase):
    """
    Schema for updating a task.
    """

    pass
