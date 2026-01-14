# Guía del Sistema de Auditoría (Audit System)

## 1. Introducción

El **Sistema de Auditoría** de `fastapi-product` es un componente crítico de nivel empresarial diseñado para proporcionar visibilidad completa sobre **quién** hizo **qué**, **cuándo** y **con qué resultado**.

Este sistema cumple con estándares de seguridad y cumplimiento (compliance) al registrar tanto el acceso a los recursos (Access Logs) como los cambios en los datos (Data Audit / CDC).

---

## 2. Arquitectura Teórica

El sistema opera en tres niveles complementarios:

### Nivel 1: Auditoría de Acceso (Access Logging)
*   **Componente**: `app/core/audit_middleware.py`
*   **Responsabilidad**: Registrar cada petición HTTP que llega al servidor.
*   **Datos Capturados**: Usuario (ID/Username), IP, Endpoint, Método HTTP (GET, POST, etc.), User Agent y Código de Estado (200, 403, 500).
*   **Propósito**: Seguridad y Trazabilidad de uso. Detecta intentos de acceso no autorizado o patrones de uso anómalos.
*   **Almacenamiento**: Tabla `audit_log` (Acción: `ACCESS`).

### Nivel 2: Auditoría de Datos (Data Audit / CDC)
*   **Componente**: `app/core/audit_hooks.py`
*   **Responsabilidad**: Detectar cambios en la base de datos (INSERT, UPDATE, DELETE) de manera automática.
*   **Tecnología**: SQLAlchemy Event Hooks (`after_flush`).
*   **Datos Capturados**:
    *   **CREATE**: Captura el snapshot inicial del objeto.
    *   **UPDATE**: Captura el "Diff" (Valor Anterior vs Valor Nuevo) solo de los campos modificados.
    *   **DELETE**: Registra qué entidad fue eliminada.
*   **Propósito**: Integridad de datos e historial de cambios. Permite responder "¿Quién cambió el precio de este producto?" o "¿Cuál era el valor antes?".
*   **Almacenamiento**: Tabla `audit_log` (Acción: `CREATE`, `UPDATE`, `DELETE`).

### Nivel 3: Almacenamiento en Frío (Cold Storage)
*   **Componente**: `scripts/archive_audit.py`
*   **Responsabilidad**: Mantener la base de datos ligera y performante.
*   **Funcionamiento**: Mueve registros antiguos (ej. > 90 días) de la base de datos principal a archivos comprimidos (`.json.gz`) para almacenamiento a largo plazo.

---

## 3. Guía para Desarrolladores

### 3.1. Creando Nuevos Endpoints
Por defecto, **todo nuevo endpoint está auditado**. No necesitas hacer nada extra.
El `AuditMiddleware` interceptará automáticamente las peticiones y registrará el acceso.

### 3.2. Excluyendo Endpoints (No Auditar)
A veces, ciertos endpoints generan demasiado ruido y no aportan valor de seguridad (ej. `healthcheck`, endpoints de métricas, o búsquedas autocompletadas masivas). Tienes dos formas de excluirlos:

#### A. Exclusión Global (Vía `.env`)
Ideal para rutas estáticas o prefijos completos.
Edita `AUDIT_EXCLUDED_PATHS` en tu archivo `.env`:

```json
AUDIT_EXCLUDED_PATHS='["/docs", "/openapi.json", "GET:/api/public-data"]'
```
*   `/docs`: Excluye todo lo que empiece por `/docs`.
*   `GET:/api/public-data`: Excluye solo el método GET en esa ruta.

#### B. Exclusión Puntual (Vía Código)
Ideal para lógica específica dentro de un router. Usa la dependencia `skip_access_audit`.

```python
from app.core.audit import skip_access_audit
from fastapi import APIRouter, Depends

router = APIRouter()

@router.get("/heavy-traffic", dependencies=[Depends(skip_access_audit)])
async def heavy_traffic_endpoint():
    return {"msg": "No auditado"}
```

### 3.3. Nuevos Modelos de Base de Datos
Al crear un nuevo modelo con `SQLModel`, la auditoría de datos (Hooks) funcionará automáticamente siempre que uses la `Session` estándar de la aplicación.

**Requisito Importante**: Asegúrate de que tu modelo herede de `SQLModel` y sea parte de la metadata importada en `alembic/env.py`.

---

## 4. Estructura de la Base de Datos (`audit_log`)

| Columna | Tipo | Descripción |
| :--- | :--- | :--- |
| `id` | Integer | Identificador único. |
| `user_id` | Integer | ID del usuario que realizó la acción (o NULL si es Anónimo/Sistema). |
| `username` | String | Username capturado en el momento ( redundancia útil por si el user se borra). |
| `action` | String | `ACCESS`, `CREATE`, `UPDATE`, `DELETE`. |
| `entity_type` | String | Nombre del Modelo (ej. `Task`, `Product`) o `Endpoint` para accesos. |
| `entity_id` | String | ID de la entidad afectada o Path del endpoint. |
| `changes` | JSON | Diff de cambios (`old` vs `new`) o metadatos del request. |
| `ip_address` | String | Dirección IP del cliente. |
| `user_agent` | String | Navegador o cliente HTTP utilizado. |
| `timestamp` | Datetime | Fecha y hora exacta (UTC recomendado). |

**Ejemplo de JSON en `changes` (UPDATE):**
```json
{
  "price": {
    "old": "100.00",
    "new": "120.50"
  },
  "status": {
    "old": "active",
    "new": "archived"
  }
}
```

---

## 5. Pros y Contras

### Pros
*   **Cumplimiento Total**: Trazabilidad completa de acciones y datos.
*   **Diagnóstico**: Facilita enormemente el debugging de "quién rompió esto".
*   **Desacoplado**: Los desarrolladores no necesitan escribir código de "log" en sus servicios; sucede "mágicamente".

### Contras
*   **Volumen de Datos**: La tabla `audit_log` crece MUY rápido (aprox. 2-5x el volumen de transacciones + accesos).
    *   *Solución*: Configurar correctamente el script de archivado (`Cold Storage`).
*   **Performance**: Hay un ligero overhead en cada escritura (Hooks) y lectura (Middleware). En la mayoría de aplicaciones empresariales es imperceptible, pero en sistemas de *high-frequency trading*, se debería revisar.

---

## 6. Mantenimiento y Operaciones

### Archivo de Logs (Cold Storage)
Se debe configurar un **Cron Job** (tarea programada) en el servidor para ejecutar el script de limpieza periódicamente (ej. cada noche a las 3 AM).

```bash
# Ejemplo de ejecución manual (archivar logs de más de 30 días)
python scripts/archive_audit.py --days 30 --dir /mnt/backups/audit
```

---

## 7. Solución de Problemas (Troubleshooting)

### Problema: El usuario aparece como `N/A` o `None` en los Logs de Datos (Hooks)
*   **Causa**: Los Hooks de SQLAlchemy corren en un nivel profundo del ORM y a veces pierden el contexto de la petición web, especialmente en tareas asíncronas o scripts fuera de FastAPI.
*   **Solución**: El sistema usa `ContextVars` (`app/core/audit.py`) para propagar el usuario. Asegúrate de que la operación de escritura ocurra dentro del ciclo de vida de una petición (request) donde el `AuditMiddleware` haya corrido. Si es un script manual (como un seed), el usuario será `None` por diseño a menos que lo inyectes manualmente.

### Problema: La base de datos está muy lenta
*   **Causa**: La tabla `audit_log` tiene millones de registros.
*   **Solución**: Ejecuta el script de `archive_audit.py` inmediatamente para mover datos viejos. Considera añadir particionamiento a la tabla `audit_log` en PostgreSQL si el volumen es extremo.
