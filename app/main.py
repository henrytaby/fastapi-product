import os
import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.db import create_db_and_tables
from app.core.routers import router as api_router 

app = FastAPI()

version = "v1"

description = """
API de un Sistema de tareas y productos, usando FastApi con Python.

Funciones;
- Crear, Leer, Actualizar y eliminar Tareas
"""
app = FastAPI(
    lifespan=create_db_and_tables,
    title="AppTransactionFastAPI",
    description=description,
    version=version,
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
)

# Habilitar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Prueba con "*" temporalmente
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos
    allow_headers=["*"],  # Permitir todos los encabezados
)

#version_prefix = f"/api/{version}"
version_prefix = "/api"
# Incluir el router principal
app.include_router(api_router)

# Exception Handlers
from app.core.exceptions import NotFoundException, BadRequestException, InternalServerErrorException
from app.core.handlers import not_found_exception_handler, bad_request_exception_handler, internal_server_error_handler

app.add_exception_handler(NotFoundException, not_found_exception_handler)
app.add_exception_handler(BadRequestException, bad_request_exception_handler)
app.add_exception_handler(InternalServerErrorException, internal_server_error_handler)


@app.get("/")
async def read_items():
    return FileResponse("./app/index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)