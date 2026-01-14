from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.auth.permissions import PermissionAction, PermissionChecker
from app.auth.schemas import UserModulePermission
from app.core.db import get_session

from .models import Task
from .repository import TaskRepository
from .schemas import TaskCreate, TaskUpdate
from .service import TaskService

router = APIRouter()


def get_service(session: Session = Depends(get_session)):
    repository = TaskRepository(session)
    return TaskService(repository)


# CREATE - Crear una nueva tarea
# ----------------------
@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    service: TaskService = Depends(get_service),
    _: UserModulePermission = Depends(
        PermissionChecker(
            module_slug="tasks", required_permission=PermissionAction.CREATE
        )
    ),
):
    """
    Create a new task.
    """
    return service.create_task(task_data)


# GET ONE - Obtener una tarea por ID
# ----------------------
@router.get("/{task_id}", response_model=Task)
async def get_task(
    task_id: int,
    service: TaskService = Depends(get_service),
    _: UserModulePermission = Depends(
        PermissionChecker(
            module_slug="tasks", required_permission=PermissionAction.READ
        )
    ),
):
    """
    Get a task by ID.
    """
    return service.get_task(task_id)


# UPDATE - Actualizar una tarea existente
# ----------------------
@router.patch("/{task_id}", response_model=Task, status_code=status.HTTP_201_CREATED)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    service: TaskService = Depends(get_service),
    _: UserModulePermission = Depends(
        PermissionChecker(
            module_slug="tasks", required_permission=PermissionAction.UPDATE
        )
    ),
):
    """
    Update an existing task.
    """
    return service.update_task(task_id, task_data)


# GET ALL TASK - Obtener todas las tareas
# ----------------------
@router.get("/", response_model=list[Task])
async def get_tasks(
    service: TaskService = Depends(get_service),
    _: UserModulePermission = Depends(
        PermissionChecker(
            module_slug="tasks", required_permission=PermissionAction.READ
        )
    ),
):
    """
    Get all tasks.
    """
    return service.get_tasks()


# DELETE - Eliminar una tarea
# ----------------------
@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    service: TaskService = Depends(get_service),
    _: UserModulePermission = Depends(
        PermissionChecker(
            module_slug="tasks", required_permission=PermissionAction.DELETE
        )
    ),
):
    """
    Delete a task by ID.
    """
    return service.delete_task(task_id)
