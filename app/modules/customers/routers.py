from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.auth.utils import get_current_user
from app.core.db import get_session
from app.models.user import User

from .models import Customer
from .repository import CustomerRepository
from .schemas import CustomerCreate, CustomerUpdate
from .service import CustomerService

router = APIRouter()


def get_service(session: Session = Depends(get_session)):
    repository = CustomerRepository(session)
    return CustomerService(repository)


# CREATE - Crear una nueva tarea
# ----------------------
@router.post("/", response_model=Customer, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer_data: CustomerCreate,
    service: CustomerService = Depends(get_service),
    current_user: User = Depends(get_current_user),
):
    return service.create_customer(customer_data)


# GET ONE - Obtener una tarea por ID
# ----------------------
@router.get("/{customer_id}", response_model=Customer)
async def get_customer(
    customer_id: int,
    service: CustomerService = Depends(get_service),
    current_user: User = Depends(get_current_user),
):
    return service.get_customer(customer_id)


# UPDATE - Actualizar una tarea existente
# ----------------------
@router.patch(
    "/{customer_id}", response_model=Customer, status_code=status.HTTP_201_CREATED
)
async def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    service: CustomerService = Depends(get_service),
):
    return service.update_customer(customer_id, customer_data)


# GET ALL TASK - Obtener todas las tareas
# ----------------------
@router.get("/", response_model=list[Customer])
async def get_customers(
    service: CustomerService = Depends(get_service),
    current_user: User = Depends(get_current_user),
):
    return service.get_customers()


# DELETE - Eliminar una tarea
# ----------------------
@router.delete("/{customer_id}")
async def delete_customer(
    customer_id: int, service: CustomerService = Depends(get_service)
):
    return service.delete_customer(customer_id)
