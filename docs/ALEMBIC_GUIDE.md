# Guía de Migraciones con Alembic

Esta guía explica cómo gestionar las migraciones de base de datos en el proyecto usando Alembic. Su objetivo es prevenir errores comunes como `UndefinedTable`.

## ⚠️ Regla Crítica: Registra Tus Modelos

**Antes de generar una migración**, DEBES registrar tus clases SQLModel en `alembic/env.py`.

Alembic necesita "ver" tus modelos para detectar cambios. Si no los importas en `env.py`, Alembic pensará que las tablas no existen o no detectará tus nuevos modelos, resultando en migraciones vacías o tablas faltantes.

**Archivo:** `alembic/env.py`
```python
# Importa todos los modelos para poblar SQLModel.metadata
from app.models.user import User, UserRevokedToken, ...
from app.models.role import Role, RoleModule
from app.models.module import Module, ModuleGroup
# [NUEVO] Agrega tu modelo aquí:
from app.modules.my_new_module.models import MyNewModel
```

---

## 👨‍💻 Recetas para Desarrolladores

### Receta 1: Agregando un Nuevo Módulo (Nuevas Tablas)
Has creado una nueva carpeta de módulo `app/modules/inventory` y definido un modelo `Product` en `app/modules/inventory/models.py`.

**Pasos:**
1.  **Definir el Modelo:** Asegúrate de que tu clase herede de `BaseModel` (o `SQLModel`) y tenga `table=True`.
    ```python
    class Product(BaseModel, table=True):
        ...
    ```
2.  **Registrar en `env.py`:** abre `alembic/env.py` y agrega:
    ```python
    from app.modules.inventory.models import Product
    ```
3.  **Generar Migración:**
    Ejecuta el siguiente comando en tu terminal (asegúrate de que el entorno virtual esté activo):
    ```bash
    alembic revision --autogenerate -m "Agregar tabla de productos de inventario"
    ```
4.  **Verificar Migración:**
    Revisa el archivo generado en `alembic/versions/`.
    *   ✅ **Bien:** Ves `op.create_table('product', ...)`
    *   ❌ **Mal:** Ves `def upgrade(): pass` (Migración vacía). **Solución:** Vuelve al Paso 2.
5.  **Aplicar Migración:**
    ```bash
    alembic upgrade head
    ```

### Receta 2: Modificando un Modelo Existente
Quieres agregar una columna `stock_count` al modelo existente `Product`.

**Pasos:**
1.  **Modificar el Código:**
    En `app/modules/inventory/models.py`:
    ```python
    stock_count: int = Field(default=0)
    ```
2.  **Generar Migración:**
    ```bash
    alembic revision --autogenerate -m "Agregar stock_count a producto"
    ```
3.  **Verificar y Aplicar:**
    Revisa el archivo buscando `op.add_column(...)` y ejecuta `alembic upgrade head`.

### Error Común: `UndefinedTable`
Si ves un error como `psycopg2.errors.UndefinedTable: relation "product" does not exist`, significa:
1.  Definiste la clase en Python.
2.  **PERO** olvidaste ejecutar la migración (u olvidaste registrarla en `env.py` antes de generarla).
    
**Solución:** Revisa `alembic/env.py`, regenera la migración si es necesario, y ejecuta `alembic upgrade head`.
