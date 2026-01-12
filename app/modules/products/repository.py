from typing import List, Optional

from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.core.repository import BaseRepository
from app.modules.products.models import Product

from ..catalog.products_category.models import ProductCategory


class ProductRepository(BaseRepository[Product]):
    def __init__(self, session: Session):
        super().__init__(session, Product)

    def get_all_with_relations(
        self, offset: int = 0, limit: int = 100
    ) -> List[Product]:
        statement = (
            select(Product)
            .options(selectinload(Product.category))
            .options(selectinload(Product.brand))
            .offset(offset)
            .limit(limit)
        )
        return self.session.exec(statement).all()

    def get_by_id_with_relations(self, id: int) -> Optional[Product]:
        statement = (
            select(Product)
            .where(Product.id == id)
            .options(selectinload(Product.category))
            .options(selectinload(Product.brand))
        )
        return self.session.exec(statement).first()

    def check_category_exists(self, category_id: int) -> bool:
        return self.session.get(ProductCategory, category_id) is not None
