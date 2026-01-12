# Guía de Autenticación y Seguridad (Enterprise)

Esta guía detalla la arquitectura de seguridad del sistema, basada en estándares modernos (OAuth2, JWT, Token Rotation) y diseñada para escalabilidad y robustez bancaria.

Está dirigida tanto a **Desarrolladores Backend** (para implementación de seguridad en módulos) como a **Desarrolladores Frontend** (para la correcta integración del cliente).

---

## 🏗️ Arquitectura de Seguridad

El sistema utiliza una arquitectura **Stateless** (sin estado) basada en **JWT (JSON Web Tokens)** con las siguientes características de seguridad reforzada:

1.  **Access Token**: Token JWT de vida corta (ej. 15 min). Se envía en cada petición (`Authorization: Bearer <token>`).
2.  **Refresh Token**: Token de vida larga (ej. 7 días). Se usa *únicamente* para obtener nuevos Access Tokens cuando el anterior expira.
3.  **Token Rotation (RTR)**: Cada vez que se usa un Refresh Token, este se **elimina** (invalida) y se entrega uno nuevo. Esto previene el robo de sesión persistente.
4.  **Blacklist (Revocación)**: Tabla en base de datos (`UserRevokedToken`) para "matar" tokens inmediatamente (Logout o robo detectado).
5.  **Hashing Robusto**: Contraseñas almacenadas con `bcrypt`.

---

## 🔄 Flujos de Funcionamiento (Diagramas)

### 1. Login (Inicio de Sesión)

```mermaid
sequenceDiagram
    participant FE as Frontend (Cliente)
    participant API as API (Auth Service)
    participant DB as Base de Datos

    FE->>API: POST /api/auth/token (username, password)
    API->>DB: Verificar credenciales (bcrypt)
    alt Credenciales Válidas
        API->>DB: Registrar Intento Exitoso (Log)
        API-->>FE: 200 OK { access_token, refresh_token }
    else Credenciales Inválidas
        API->>DB: Registrar Intento Fallido
        API-->>FE: 401 Unauthorized
    end
```

### 2. Petición Protegida

```mermaid
sequenceDiagram
    participant FE as Frontend
    participant API as API (Middleware/Dependency)
    participant DB as Base de Datos

    FE->>API: GET /api/products (Header: "Bearer eyJhbG...")
    API->>API: Validar Firma y Expiración JWT
    API->>DB: ¿Token en Blacklist? (UserRevokedToken)
    alt Token Válido
        API-->>FE: 200 OK (Data)
    else Token Expirado/Inválido
        API-->>FE: 401 Unauthorized
    end
```

### 3. Renovación de Token (Rotation)

Este flujo se ejecuta automáticamente en el Frontend cuando recibe un 401 o detecta que el Access Token expiró.

```mermaid
sequenceDiagram
    participant FE as Frontend
    participant API as API
    participant DB as Base de Datos

    FE->>API: POST /api/auth/token/refresh (refresh_token_viejo)
    API->>DB: ¿Refresh Token en Blacklist?
    API->>DB: Revocar (Blacklist) refresh_token_viejo
    API-->>FE: 200 OK { access_token_NUEVO, refresh_token_NUEVO }
    
    Note right of FE: Frontend debe reemplazar AMBOS tokens <br/>en su almacenamiento.
```

### 4. Logout (Cierre de Sesión Seguro)

```mermaid
sequenceDiagram
    participant FE as Frontend
    participant API as API
    participant DB as Base de Datos

    FE->>API: POST /api/auth/logout (Body: refresh_token)
    Note right of API: Header tiene Access Token
    API->>DB: Blacklist Access Token
    API->>DB: Blacklist Refresh Token
    API-->>FE: 200 OK "Successfully logged out"
```

---

## 👨‍💻 Guía para Backend (Implementación)

### Cómo proteger una ruta nueva
Para asegurar que un endpoint solo sea accesible por usuarios autenticados, inyecta la dependencia `get_current_user`.

```python
from fastapi import APIRouter, Depends
from app.auth.utils import get_current_user
from app.auth.schemas import User

router = APIRouter()

@router.get("/mi-endpoint-seguro")
def secure_data(current_user: User = Depends(get_current_user)):
    # Si llega aquí, el usuario es válido y está autenticado.
    # 'current_user' contiene los datos del usuario (id, username, roles, etc.)
    return {"message": f"Hola {current_user.username}, tienes acceso."}
```

### Cómo obtener el usuario actual
La variable `current_user` inyectada ya contiene el modelo `User` validado. Úsala para lógica de negocio (ej. filtrar datos por `current_user.id`).

---

## 🎨 Guía para Frontend (Integración)

### 1. Almacenamiento de Tokens
*   **Access Token**: Guardar en memoria (variable de estado) o `HttpOnly Cookie` (si es posible). Evitar `localStorage` si se maneja información muy sensible (XSS risk), aunque es aceptable para apps estándar si se sanitizan inputs.
*   **Refresh Token**: Guardar en `HttpOnly Cookie` (Recomendado) o almacenamiento seguro cifrado.

### 2. Interceptores (Axios / Fetch)
El frontend debe implementar un **Interceptor HTTP** para manejar la rotación transparente:

1.  Hacer petición normal con `Access Token`.
2.  Si respuesta es `401 Unauthorized`:
    *   **Pausar** peticiones pendientes.
    *   Llamar a `/api/auth/token/refresh` con el `Refresh Token` actual.
    *   Si Refresh es exitoso:
        *   Guardar **nuevos** tokens.
        *   Reintentar la petición original con el nuevo token.
    *   Si Refresh falla (401/403):
        *   **Forzar Logout** (redirigir a Login).

### 3. Logout
Siempre llamar al endpoint de logout enviando el `refresh_token` en el body para asegurar que la sesión se invalide completamente en el servidor.

```javascript
// Ejemplo de llamada Logout
await api.post('/auth/logout', {
  refresh_token: currentRefreshToken
});
// Luego limpiar storage local
```
