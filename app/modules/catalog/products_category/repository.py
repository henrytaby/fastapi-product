from sqlmodel import Session
from app.core.repository import BaseRepository
from app.modules.catalog.products_category.models import ProductCategory

class ProductCategoryRepository(BaseRepository[ProductCategory]):
    def __init__(self, session: Session):
        super().__init__(session, ProductCategory)
