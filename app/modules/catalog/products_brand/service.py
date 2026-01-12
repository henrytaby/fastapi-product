from fastapi import HTTPException, status
from .models import ProductBrand
from .schemas import ProductBrandCreate, ProductBrandUpdate
from .repository import ProductBrandRepository

class ProductBrandService:
    no_task:str = "Brand doesn't exits"
    
    def __init__(self, repository: ProductBrandRepository):
        self.repository = repository

    # CREATE
    # ----------------------
    def create_product_brand(self, item_data: ProductBrandCreate):
        item_db = ProductBrand.model_validate(item_data.model_dump())
        return self.repository.create(item_db)

    # GET ONE
    # ----------------------
    def get_product_brand(self, item_id: int):
        item_db = self.repository.get_by_id(item_id)
        if not item_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=self.no_task
            )
        return item_db

    # UPDATE
    # ----------------------
    def update_product_brand(self, item_id: int, item_data: ProductBrandUpdate):
        item_data_dict = item_data.model_dump(exclude_unset=True)
        updated_item = self.repository.update(item_id, item_data_dict)
        
        if not updated_item:
             raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=self.no_task
            )
        return updated_item

    # GET ALL PLANS
    # ----------------------
    def get_product_brands(self, offset: int = 0, limit: int = 100):
        return self.repository.get_all(offset, limit)

    # DELETE
    # ----------------------
    def delete_product_brand(self, item_id: int):
        success = self.repository.delete(item_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=self.no_task
            )
        return {"detail": "ok"}
