# Guía de Testing Automatizado (Backend)

Esta guía documenta los estándares, herramientas y buenas prácticas para escribir y ejecutar pruebas automatizadas en el backend del proyecto.

> **Filosofía**: Priorizamos **Tests de Integración** que validan el flujo completo (Router -> Service -> DB) utilizando una base de datos real (SQLite en memoria) para garantizar confiabilidad y velocidad.

---

## 🛠️ Herramientas

*   **Framework**: `pytest` (Estándar de facto en Python).
*   **Cliente HTTP**: `TestClient` (de FastAPI/Starlette) para simular peticiones.
*   **Base de Datos**: `SQLite` (In-Memory) para pruebas aisladas y rápidas.

---

## ⚙️ Configuración del Entorno (`conftest.py`)

El archivo `tests/conftest.py` es el corazón de nuestro sistema de pruebas. Configura automáticamente el entorno antes de cada test.

### Fixtures Principales

1.  **`session`**:
    *   Crea una base de datos **SQLite en memoria** (`sqlite://`).
    *   Ejecuta `SQLModel.metadata.create_all(engine)` para crear todas las tablas definidas en los modelos.
    *   Entrega una sesión de base de datos activa.
    *   Al finalizar el test, la base de datos se destruye (garantizando aislamiento).

2.  **`client`**:
    *   Crea una instancia de `TestClient(app)`.
    *   **Sobrescribe la dependencia de base de datos** (`app.dependency_overrides[get_session]`) para que la aplicación use la base de datos de prueba en lugar de PostgreSQL.

3.  **`superuser`**:
    *   Crea un usuario administrador en la base de datos de prueba (`username="superuser"`, `password="password"`).
    *   Útil si necesitas relacionar datos con un usuario existente.

4.  **`superuser_token_headers`**:
    *   Realiza un login real contra el endpoint `/api/auth/token` usando el usuario `superuser`.
    *   Devuelve un diccionario: `{"Authorization": "Bearer <token>"}`.
    *   Este es el fixture que usarás en el 90% de los tests de endpoints protegidos.

---

## 🚀 Ejecución de Tests

Desde la raíz del proyecto (asegúrate de tener el entorno virtual activado):

```bash
# Ejecutar todos los tests
pytest

# Ejecutar con salida detallada (ver nombres de tests)
pytest -v

# Ejecutar tests que coincidan con un nombre específico (ej: "create")
pytest -k "create"

# Ejecutar y detenerse al primer fallo
pytest -x
```

---

## ✍️ Cómo escribir un Test

Crea un archivo nuevo en `tests/` o `tests/modules/` (ej: `test_products.py`). El nombre del archivo debe empezar con `test_`.

### 1. Test Básico (Create)

Inyecta el fixture `client` para hacer peticiones.

```python
def test_create_product(client):
    response = client.post(
        "/api/products/",
        json={"name": "Laptop Gamer", "price": 1500.0, "stock": 10}
    )
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "Laptop Gamer"
    assert "id" in data
```

### 2. Test con Verificación en Base de Datos

Inyecta `session` si necesitas consultar la BD directamente para verificar el estado.

```python
from sqlmodel import select
from app.modules.products.models import Product

def test_delete_product(client, session):
    # 1. Crear dato previo (Seed)
    product = Product(name="Borrar", price=10)
    session.add(product)
    session.commit()
    session.refresh(product)

    # 2. Ejecutar acción
    response = client.delete(f"/api/products/{product.id}")

    # 3. Verificar respuesta
    assert response.status_code == 200

    # 4. Verificar en BD (debería no existir)
    deleted_product = session.get(Product, product.id)
    assert deleted_product is None
```

---

## 🛡️ Testing de Autenticación

Para probar endpoints protegidos, hay dos estrategias:

### Estrategia A: Usando el Fixture `superuser_token_headers` (Recomendada)
Esta es la forma más rápida y limpia. El fixture `superuser_token_headers` ya realiza el login de un usuario con permisos de superadministrador y te devuelve el diccionario de headers listo para usar.

```python
def test_create_secure_item(client, superuser_token_headers):
    response = client.post(
        "/api/items/",
        json={"name": "Secure Item"},
        headers=superuser_token_headers  # <--- Inyectar headers aquí
    )
    assert response.status_code == 201
```

### Estrategia B: Override de Auth (Mocking)
Útil si quieres probar roles específicos sin pasar por el login real o si quieres simular usuarios con permisos limitados.

```python
from app.auth.utils import get_current_user
from app.models.user import User

def test_protected_route_mock(client, app):
    # Usuario mock
    mock_user = User(id=1, username="testuser", is_superuser=True)
    
    # Sobrescribir dependencia
    app.dependency_overrides[get_current_user] = lambda: mock_user

    response = client.get("/api/users/me")
    assert response.status_code == 200
    
    # Limpiar
    app.dependency_overrides = {}
```

### Estrategia C: Login Real Manual
Si necesitas probar el flujo de login explícitamente o loguearte con un usuario normal (no superuser), puedes usar el helper `get_authorization_headers` en `conftest.py` o hacerlo manualmente en el test.

---

## ✅ Checklist de Calidad
Antes de subir código, asegúrate de:
1.  Si agregaste lógica nueva, agregaste un test.
2.  Si corregiste un bug, agregaste un test que reproduzca el bug (prevent regression).
3.  Todos los tests pasan (`pytest` verde).
