from sqlmodel import Session
from app.core.repository import BaseRepository
from app.modules.tasks.models import Task

class TaskRepository(BaseRepository[Task]):
    def __init__(self, session: Session):
        super().__init__(session, Task)
