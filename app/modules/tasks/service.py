from fastapi import HTTPException, status
from sqlmodel import select, Session
from .models import Task
from .schemas import TaskCreate, TaskUpdate

class TaskService:
    no_task:str = "Task doesn't exits"
    # CREATE
    # ----------------------
    def create_task(self, item_data: TaskCreate, session: Session):
        task_db = Task.model_validate(item_data.model_dump())
        session.add(task_db)
        session.commit()
        session.refresh(task_db)
        return task_db

    # GET ONE
    # ----------------------
    def get_task(self, item_id: int, session: Session):
        task_db = session.get(Task, item_id)
        if not task_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=self.no_task
            )
        return task_db

    # UPDATE
    # ----------------------
    def update_task(self, item_id: int, item_data: TaskUpdate, session: Session):
        task_db = session.get(Task, item_id)
        if not task_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=self.no_task
            )
        item_data_dict = item_data.model_dump(exclude_unset=True)
        task_db.sqlmodel_update(item_data_dict)
        session.add(task_db)
        session.commit()
        session.refresh(task_db)
        return task_db

    # GET ALL PLANS
    # ----------------------
    def get_tasks(self, session: Session):
        return session.exec(select(Task)).all()
        
    # DELETE
    # ----------------------
    def delete_task(self, item_id: int, session: Session):
        task_db = session.get(Task, item_id)
        if not task_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=self.no_task
            )
        session.delete(task_db)
        session.commit()
        return {"detail": "ok"}
