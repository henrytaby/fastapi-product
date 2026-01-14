import uuid
from contextlib import asynccontextmanager

import structlog
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html
from fastapi.responses import FileResponse

from app.core.config import settings
from app.core.db import create_db_and_tables
from app.core.exceptions import (
    BadRequestException,
    InternalServerErrorException,
    NotFoundException,
)
from app.core.handlers import (
    bad_request_exception_handler,
    internal_server_error_handler,
    not_found_exception_handler,
)
from app.core.logging import configure_logging
from app.core.routers import router as api_router
from app.core.audit_middleware import AuditMiddleware
from app.core.audit_hooks import register_audit_hooks
from app.core.db import engine

# Setup Logging
configure_logging()

description = """
API de un Sistema de tareas y productos, usando FastApi con Python.

Funciones;
- Crear, Leer, Actualizar y eliminar Tareas
"""
# ... existing imports ...

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    register_audit_hooks(engine)
    yield


app = FastAPI(
    lifespan=lifespan,
    title=settings.PROJECT_NAME,
    description=description,
    version=settings.VERSION,
    redoc_url=None,  # Disable default Redoc to customize CDN
    license_info={"name": "MIT License", "url": "https://opensource.org/license/mit"},
    contact={
        "name": "Henry Alejandro Taby Zenteno",
        "url": "https://github.com/henrytaby",
        "email": "henry.taby@gmail.com",
    },
    openapi_tags=[
        {
            "name": "Tasks",
            "description": "Lista de Tareas",
        },
        {
            "name": "Products",
            "description": "Lista de Products",
        },
        {
            "name": "Customers",
            "description": "Lista de Customers",
        },
    ],
    openapi_url="/openapi.json",
)

# Habilitar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Prueba con "*" temporalmente
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos
    allow_headers=["*"],  # Permitir todos los encabezados
)
app.add_middleware(AuditMiddleware)


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id=request_id)

    response = await call_next(request)
    return response


# version_prefix = f"/api/{version}"
version_prefix = "/api"
# Incluir el router principal
app.include_router(api_router, prefix=version_prefix)


app.add_exception_handler(NotFoundException, not_found_exception_handler)  # type: ignore
app.add_exception_handler(BadRequestException, bad_request_exception_handler)  # type: ignore
app.add_exception_handler(InternalServerErrorException, internal_server_error_handler)  # type: ignore


@app.get("/")
async def read_items():
    return FileResponse("./app/index.html")


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="https://unpkg.com/redoc@latest/bundles/redoc.standalone.js",
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
