from .models import Product
from .schemas import ProductCreate, ProductUpdate
from .repository import ProductRepository
from app.core.exceptions import NotFoundException, InternalServerErrorException

class ProductService:
    no_product:str = "Product doesn't exits"
    
    def __init__(self, repository: ProductRepository):
        self.repository = repository

    # CREATE
    # ----------------------
    def create_product(self, item_data: ProductCreate):

        # Validate Category
        if not self.repository.check_category_exists(item_data.category_id):
             raise NotFoundException(detail=f"Category Id:{item_data.category_id} doesn't exist")
            
        product_db = Product.model_validate(item_data.model_dump())
        
        try:
            return self.repository.create(product_db)
        except Exception:
            raise InternalServerErrorException(detail="Internal Server error, create Product")

    # GET ONE
    # ----------------------
    def get_product(self, item_id: int):
        product_db = self.repository.get_by_id_with_relations(item_id)

        if not product_db:
            raise NotFoundException(detail=self.no_product)
        return product_db

    # UPDATE
    # ----------------------
    def update_product(self, item_id: int, item_data: ProductUpdate):
        item_data_dict = item_data.model_dump(exclude_unset=True)
        updated_product = self.repository.update(item_id, item_data_dict)
        
        if not updated_product:
             raise NotFoundException(detail=self.no_product)
        return updated_product

    # GET ALL PLANS
    # ----------------------
    def get_products(self, offset: int = 0, limit: int = 100):
        return self.repository.get_all_with_relations(offset, limit)

    # DELETE
    # ----------------------
    def delete_product(self, item_id: int):
        success = self.repository.delete(item_id)
        if not success:
            raise NotFoundException(detail=self.no_product)
        return {"detail": "ok"}
