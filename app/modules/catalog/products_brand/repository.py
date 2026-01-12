from sqlmodel import Session

from app.core.repository import BaseRepository
from app.modules.catalog.products_brand.models import ProductBrand


class ProductBrandRepository(BaseRepository[ProductBrand]):
    def __init__(self, session: Session):
        super().__init__(session, ProductBrand)
