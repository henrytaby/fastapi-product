from fastapi import APIRouter, status, Depends
from sqlmodel import Session
from app.core.db import get_session
from .models import ProductBrand
from .schemas import ProductBrandCreate, ProductBrandUpdate
from .service import ProductBrandService
from .repository import ProductBrandRepository

router = APIRouter()

def get_service(session: Session = Depends(get_session)):
    repository = ProductBrandRepository(session)
    return ProductBrandService(repository)


# CREATE - Crear una nueva tarea
# ----------------------
@router.post("/", response_model=ProductBrand, status_code=status.HTTP_201_CREATED)
async def create_product_brand(
    product_brand_data: ProductBrandCreate,
    service: ProductBrandService = Depends(get_service)
    ):
    return service.create_product_brand(product_brand_data)

# GET ONE - Obtener una tarea por ID
# ----------------------
@router.get("/{product_brand_id}", response_model=ProductBrand)
async def get_product_brand(
    product_brand_id: int,
    service: ProductBrandService = Depends(get_service)
):
    return service.get_product_brand(product_brand_id)

# UPDATE - Actualizar una tarea existente
# ----------------------
@router.patch("/{product_brand_id}", response_model=ProductBrand, status_code=status.HTTP_201_CREATED)
async def update_product_brand(
    product_brand_id: int,
    product_brand_data: ProductBrandUpdate,
    service: ProductBrandService = Depends(get_service)
):
    
    return service.update_product_brand(product_brand_id, product_brand_data)

# GET ALL TASK - Obtener todas las tareas
# ----------------------
@router.get("/", response_model=list[ProductBrand])
async def get_product_brands(
    service: ProductBrandService = Depends(get_service)
):
    return service.get_product_brands()

# DELETE - Eliminar una tarea
# ----------------------
@router.delete("/{product_brand_id}")
async def delete_product_brand(
    product_brand_id: int,
    service: ProductBrandService = Depends(get_service)
):
    return service.delete_product_brand(product_brand_id)