from .models import Task
from .schemas import TaskCreate, TaskUpdate
from .repository import TaskRepository
from app.core.exceptions import NotFoundException

class TaskService:
    no_task:str = "Task doesn't exits"
    
    def __init__(self, repository: TaskRepository):
        self.repository = repository

    # CREATE
    # ----------------------
    def create_task(self, item_data: TaskCreate):
        task_db = Task.model_validate(item_data.model_dump())
        return self.repository.create(task_db)

    # GET ONE
    # ----------------------
    def get_task(self, item_id: int):
        task_db = self.repository.get_by_id(item_id)
        if not task_db:
            raise NotFoundException(detail=self.no_task)
        return task_db

    # UPDATE
    # ----------------------
    def update_task(self, item_id: int, item_data: TaskUpdate):
        item_data_dict = item_data.model_dump(exclude_unset=True)
        updated_task = self.repository.update(item_id, item_data_dict)
        
        if not updated_task:
             raise NotFoundException(detail=self.no_task)
        return updated_task

    # GET ALL PLANS
    # ----------------------
    def get_tasks(self, offset: int = 0, limit: int = 100):
        return self.repository.get_all(offset, limit)
        
    # DELETE
    # ----------------------
    def delete_task(self, item_id: int):
        success = self.repository.delete(item_id)
        if not success:
            raise NotFoundException(detail=self.no_task)
        return {"detail": "ok"}
