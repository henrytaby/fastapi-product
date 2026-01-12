# FastAPI Product & Task Management API

API RESTful construida con FastAPI para la gestión de productos, tareas, categorías y marcas.

## Descripción

Este proyecto es una API modular diseñada con buenas prácticas de ingeniería de software, enfocada en la escalabilidad y mantenibilidad. Permite gestionar:

*   **Tareas**: Control básico de tareas.
*   **Productos**: Gestión de inventario con relaciones a categorías y marcas.
*   **Clientes**: Administración de usuarios/clientes.
*   **Catálogo**: Gestión centralizada de Categorías y Marcas.

## Arquitectura

El proyecto implementa una **Arquitectura Modular** apoyada en el **Patrón Repositorio**.

### Diagrama de Flujo de Datos
```mermaid
graph LR
    A[Router] --> B[Service]
    B --> C[Repository]
    C --> D["Database (SQLModel)"]
```

### Componentes Principales

#### 1. Estructura Modular (`app/modules/`)
El código se organiza por dominios de negocio en lugar de capas técnicas. Cada módulo (`tasks`, `products`, etc.) contiene todo lo necesario para su funcionamiento:
*   `routers.py`: Definición de endpoints.
*   `service.py`: Lógica de negocio.
*   `repository.py`: Acceso a datos.
*   `models.py`: Definición de tablas.
*   `schemas.py`: Validación de entrada/salida (Pydantic).

#### 2. Patrón Repositorio (`app/core/repository.py`)
Se utiliza para desacoplar la lógica de negocio de la capa de acceso a datos.
*   **`BaseRepository`**: Clase genérica que provee métodos CRUD estándar (`create`, `get_by_id`, `update`, `delete`) para cualquier modelo.
*   **Repositorios Específicos**: (Ej: `ProductRepository`) Extienden el base para consultas complejas, como carga de relaciones o validaciones específicas.

#### 3. Inyección de Dependencias
FastAPI `Depends` se utiliza para gestionar el ciclo de vida de los componentes:
*   `get_session` inyecta la sesión de DB.
*   El `Repository` se inyecta en el `Service`.
*   El `Service` se inyecta en el `Router`.

#### 4. Manejo Centralizado de Excepciones (`app/core/handlers.py`)
El sistema captura excepciones de dominio (como `NotFoundException`) y las transforma automáticamente en respuestas JSON estandarizadas (HTTP 404, 400, 500), manteniendo limpios los servicios.

#### 5. Configuración Tipada (`app/core/config.py`)
Uso de `pydantic-settings` para cargar y validar variables de entorno desde `.env`.

## Tecnologías

*   **Python 3.10+**
*   **FastAPI**: Framework web moderno y rápido.
*   **SQLModel**: ORM que combina SQLAlchemy y Pydantic.
*   **PostgreSQL**: Base de datos relacional.
*   **Pydantic Settings**: Gestión de configuración.

## Instalación y Configuración

### 1. Requisitos Previos
*   Python 3.9+
*   PostgreSQL
*   Git

### 2. Clonar el repositorio
```bash
git clone git@github.com:henrytaby/fastapi-product.git
cd fastapi-product
```

### 3. Crear entorno virtual
```bash
python3 -m venv env
source env/bin/activate
```

### 4. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 5. Configurar Base de Datos
Crear la base de datos en PostgreSQL:
```bash
sudo su postgres
createdb fastapi_product
exit
```

Configurar variables de entorno:
```bash
cp .env.example .env
```
Editar `.env` con tus credenciales:
```env
DATABASE_URL="postgresql://user:password@localhost/fastapi_product"
SECRET_KEY=tu_clave_secreta_generada
...
```

### 6. Migraciones de Base de Datos (Alembic)
El proyecto utiliza **Alembic** para gestionar cambios en el esquema de la base de datos de forma segura.

Generar una nueva migración (tras modificar un modelo):
```bash
alembic revision --autogenerate -m "Descripción del cambio"
```

Aplicar cambios pendientes a la BD:
```bash
alembic upgrade head
```

### 7. Inicializar Datos (Seeds)
```bash
PYTHONPATH=. python3 seeds/seed_create_app.py
```

### 8. Testing Automatizado
El proyecto incluye tests de integración usando `pytest`. Las pruebas utilizan una base de datos en memoria (SQLite), por lo que no afectan los datos reales.

Ejecutar tests:
```bash
pytest
```

### 9. Calidad de Código
El proyecto utiliza herramientas estándar para asegurar la consistencia y calidad.

Linting y Formateo (Ruff):
```bash
ruff check .
ruff format .
```

### 10. Logging Estructurado
El sistema utiliza `structlog` para generar logs en formato JSON (en producción) o texto coloreado (en desarrollo), incluyendo un `request_id` único para trazabilidad.

```bash
# Los logs se mostrarán en la salida estándar (stdout)
fastapi dev app/main.py
```

## Guía de Uso para Desarrolladores

### 1. Uso del Logger
En cualquier archivo (Router, Service, Repository):
```python
import structlog
logger = structlog.get_logger()

def mi_funcion():
    # Log simple
    logger.info("iniciando_proceso")
    
    # Log con contexto (recomendado)
    logger.info("usuario_creado", user_id=123, email="test@example.com")
    
    try:
        ...
    except Exception as e:
        # Log de error con traza completa
        logger.error("error_critico", error=str(e), exc_info=True)
```

### 2. Uso de Repositorios
La inyección de dependencias se maneja en el **Router**, el **Service** recibe el repositorio ya instanciado.
```python
# Service
class TaskService:
    def __init__(self, repository: TaskRepository):
        self.repository = repository

    def get(self, id: int):
        return self.repository.get_by_id(id)

# Router
@router.post("/")
def create_task(
    item: TaskCreate, 
    service: TaskService = Depends(get_service) # Inyecta Repo automáticamente
):
    service.create(item)
```

### 3. Lanzar Excepciones
Nunca uses `HTTPException` directamente en el Service. Usa las excepciones de dominio:
```python
from app.core.exceptions import NotFoundException, BadRequestException

if not user:
    raise NotFoundException(detail="Usuario no encontrado")
```

## Ejecución

Modo desarrollo (con hot-reload):
```bash
fastapi dev app/main.py
```

La API estará disponible en: `http://localhost:8000`
Documentación interactiva: `http://localhost:8000/docs`

## Licencia

MIT