from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.core.db import get_session

from .models import Product
from .repository import ProductRepository
from .schemas import ProductCreate, ProductRead, ProductUpdate
from .service import ProductService

router = APIRouter()


def get_service(session: Session = Depends(get_session)):
    repository = ProductRepository(session)
    return ProductService(repository)


# CREATE - Crear una nueva tarea
# ----------------------
@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate, service: ProductService = Depends(get_service)
):
    return service.create_product(product_data)


# GET ONE - Obtener una tarea por ID
# ----------------------
@router.get("/{product_id}", response_model=ProductRead)
async def get_product(product_id: int, service: ProductService = Depends(get_service)):
    return service.get_product(product_id)


# UPDATE - Actualizar una tarea existente
# ----------------------
@router.patch(
    "/{product_id}", response_model=Product, status_code=status.HTTP_201_CREATED
)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    service: ProductService = Depends(get_service),
):
    return service.update_product(product_id, product_data)


# GET ALL TASK - Obtener todas las tareas
# ----------------------
@router.get("/", response_model=list[ProductRead])
async def get_products(service: ProductService = Depends(get_service)):
    return service.get_products()


# DELETE - Eliminar una tarea
# ----------------------
@router.delete("/{product_id}")
async def delete_product(
    product_id: int, service: ProductService = Depends(get_service)
):
    return service.delete_product(product_id)
