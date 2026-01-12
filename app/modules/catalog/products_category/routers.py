from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.core.db import get_session

from .models import ProductCategory
from .repository import ProductCategoryRepository
from .schemas import ProductCategoryCreate, ProductCategoryUpdate
from .service import ProductCategoryService

router = APIRouter()


def get_service(session: Session = Depends(get_session)):
    repository = ProductCategoryRepository(session)
    return ProductCategoryService(repository)


# CREATE - Crear una nueva tarea
# ----------------------
@router.post("/", response_model=ProductCategory, status_code=status.HTTP_201_CREATED)
async def create_product_category(
    product_category_data: ProductCategoryCreate,
    service: ProductCategoryService = Depends(get_service),
):
    return service.create_product_category(product_category_data)


# GET ONE - Obtener una tarea por ID
# ----------------------
@router.get("/{product_category_id}", response_model=ProductCategory)
async def get_product_category(
    product_category_id: int, service: ProductCategoryService = Depends(get_service)
):
    return service.get_product_category(product_category_id)


# UPDATE - Actualizar una tarea existente
# ----------------------
@router.patch(
    "/{product_category_id}",
    response_model=ProductCategory,
    status_code=status.HTTP_201_CREATED,
)
async def update_product_category(
    product_category_id: int,
    product_category_data: ProductCategoryUpdate,
    service: ProductCategoryService = Depends(get_service),
):
    return service.update_product_category(product_category_id, product_category_data)


# GET ALL TASK - Obtener todas las tareas
# ----------------------
@router.get("/", response_model=list[ProductCategory])
async def get_product_categories(
    service: ProductCategoryService = Depends(get_service),
):
    return service.get_product_categories()


# DELETE - Eliminar una tarea
# ----------------------
@router.delete("/{product_category_id}")
async def delete_product_category(
    product_category_id: int, service: ProductCategoryService = Depends(get_service)
):
    return service.delete_product_category(product_category_id)
