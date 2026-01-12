from sqlmodel import Session

from app.core.repository import BaseRepository
from app.modules.customers.models import Customer


class CustomerRepository(BaseRepository[Customer]):
    def __init__(self, session: Session):
        super().__init__(session, Customer)
