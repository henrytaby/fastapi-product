# FastAPI Product & Task Management API

API RESTful construida con FastAPI para la gestión de productos, tareas, categorías y marcas.

## Descripción

Este proyecto es una API modular diseñada con buenas prácticas de ingeniería de software, enfocada en la escalabilidad y mantenibilidad. Permite gestionar:

*   **Tareas**: Control básico de tareas.
*   **Productos**: Gestión de inventario con relaciones a categorías y marcas.
*   **Clientes**: Administración de usuarios/clientes.
*   **Catálogo**: Gestión centralizada de Categorías y Marcas.
*   **Seguridad**: Autenticación JWT robusta con **Rotación de Tokens**, Logout seguro (Blacklist) y Hashing de contraseñas.
*   **Auditoría**: Sistema completo de registro de accesos y cambios de datos (CDC) con almacenamiento histórico.

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
*   Python 3.10+
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

### 6. Inicializar Base de Datos (Crear Tablas)
Una vez configurada la conexión en el `.env`, ejecuta las migraciones para crear todas las tablas:
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

### 11. Seguridad y RBAC (Control de Acceso)
El sistema implementa un modelo de seguridad granular basado en **Roles** y **Módulos**:

*   **Permisos por Módulo**: El acceso se define a nivel de módulo (ej: `tasks`, `products`) usando un identificador único (`slug`).
*   **Permisos Agregados**: Un usuario puede tener múltiples roles. Sus permisos finales son la **suma** de todos los permisos de sus roles activos.
*   **Superusuario**: Un usuario con `is_superuser=True` tiene acceso total al sistema, ignorando las reglas de RBAC.
*   **Dependencia de Seguridad**: Se utiliza `PermissionChecker` para proteger endpoints:
    ```python
    # Ejemplo: Requerir permiso de CREAR en el módulo 'tasks'
    Depends(PermissionChecker(module_slug="tasks", required_permission=PermissionAction.CREATE))
    ```
*   **Menús Dinámicos**: Endpoint `/me/menu/{role_id}` genera la estructura del menú frontend permitida para el rol seleccionado.

Para detalles de implementación y recetas, ver la **[Guía de RBAC (Permisos)](docs/RBAC_GUIDE.md)**.

### 12. Manejo de Base de Datos (Alembic)
El proyecto utiliza **Alembic** para versionar la estructura de la base de datos.
**Regla Crítica**: Todo nuevo modelo (tabla) debe ser importado en `alembic/env.py` para ser detectado.

Flujo de Trabajo:
1.  **Crear Modelo**: Definir clase SQLModel en `models.py`.
2.  **Registrar**: Importar el modelo en `alembic/env.py`.
3.  **Generar Migración**: `alembic revision --autogenerate -m "nombre_cambio"`.
4.  **Aplicar**: `alembic upgrade head`.

Si encuentras el error `UndefinedTable`, es porque el modelo no se registró antes de migrar. Ver **[Guía de Alembic Migraciones](docs/ALEMBIC_GUIDE.md)**.

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

### 11. Documentación para Desarrolladores
¿Quieres profundizar en el desarrollo? Consulta nuestras guías detalladas:

1.  **[Manual del Desarrollador (Creación de Módulos)](docs/DEVELOPER_GUIDE.md)**
2.  **[Guía de Autenticación y Seguridad](docs/AUTHENTICATION_GUIDE.md)**
3.  **[Guía de Testing Automatizado](docs/TESTING_GUIDE.md)**
4.  **[Guía de Manejo de Excepciones](docs/EXCEPTION_HANDLING_GUIDE.md)**
5.  **[Guía de RBAC (Permisos)](docs/RBAC_GUIDE.md)**
6.  **[Guía de Auditoría](docs/AUDIT_GUIDE.md)**
7.  **[Guía de Alembic Migraciones](docs/ALEMBIC_GUIDE.md)**
8.  **[Guía de Calidad de Código (Linting & Typing)](docs/QUALITY_GUIDE.md)**
## Ejecución

Modo desarrollo (con hot-reload):
```bash
fastapi dev app/main.py
```

La API estará disponible en: `http://localhost:8000`
- **[API Documentation](http://localhost:8000/docs)**: Swagger UI for interactive API testing.

## Licencia

MIT