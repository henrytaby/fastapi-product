from typing import Generic, TypeVar, Type, List, Optional
from sqlmodel import SQLModel, Session, select

ModelType = TypeVar("ModelType", bound=SQLModel)

class BaseRepository(Generic[ModelType]):
    def __init__(self, session: Session, model: Type[ModelType]):
        self.session = session
        self.model = model

    def get_all(self, offset: int = 0, limit: int = 100) -> List[ModelType]:
        statement = select(self.model).offset(offset).limit(limit)
        return self.session.exec(statement).all()

    def get_by_id(self, id: int) -> Optional[ModelType]:
        return self.session.get(self.model, id)

    def create(self, obj: ModelType) -> ModelType:
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def update(self, id: int, obj_data: dict) -> Optional[ModelType]:
        db_obj = self.get_by_id(id)
        if not db_obj:
            return None
        
        for key, value in obj_data.items():
            setattr(db_obj, key, value)
            
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    def delete(self, id: int) -> bool:
        db_obj = self.get_by_id(id)
        if not db_obj:
            return False
        
        self.session.delete(db_obj)
        self.session.commit()
        return True
