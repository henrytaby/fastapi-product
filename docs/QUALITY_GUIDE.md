# Guía de Calidad de Código (Linting & Typing)

## 1. Introducción

En este proyecto, mantenemos un estándar alto de calidad de código utilizando herramientas automatizadas de última generación. El objetivo es:
1.  **Uniformidad**: Que todo el código parezca escrito por una sola persona.
2.  **Prevención de Errores**: Detectar bugs (variables no usadas, errores de tipo) *antes* de ejecutar el código.
3.  **Velocidad**: Automatizar revisiones triviales para que los Code Reviews se enfoquen en lógica de negocio.

Las herramientas principales son **Ruff** (Linting y Formateo) y **MyPy** (Tipado Estático).

---

## 2. Ruff (Linting y Formateo)

[Ruff](https://docs.astral.sh/ruff/) es un linter y formateador de Python escrito en Rust. Es extremadamente rápido y reemplaza a múltiples herramientas antiguas (Black, Isort, Flake8).

### 2.1. ¿Para qué se usa?
*   **Linting (`ruff check`)**: Analiza el código buscando errores estilísticos (ej. líneas muy largas), imports no usados, variables indefinidas, etc.
*   **Formateo (`ruff format`)**: Reescribe automáticamente tu código para cumplir con el estilo estándar (espacios, comillas, saltos de línea). Equivalente a "Black".

### 2.2. Configuración del Proyecto (`ruff.toml`)

La configuración se encuentra en el archivo `ruff.toml`.

*   **Longitud de línea**: `88` caracteres (Estándar de la industria).
*   **Versión Python**: `3.10`.
*   **Exclusiones**: La carpeta `alembic/` (migraciones autogeneradas) está excluida.

#### Reglas Activas (`[lint] select`)
Habilitamos familias de reglas específicas:
*   `E` (pycodestyle errors): Errores de estilo básicos.
*   `W` (pycodestyle warnings): Advertencias de estilo.
*   `F` (pyflakes): Errores lógicos (variables no usadas, imports rotos).
*   **`I` (isort)**: **Ordenamiento de imports**. Ruff ordena tus imports automáticamente (Librería estándar -> Terceros -> Proyecto).
*   `B` (flake8-bugbear): Detección de patrones propensos a bugs.

#### Excepciones Importantes
*   **Ignore `B008`**: "Do not perform function calls in argument defaults".
    *   *Por qué*: FastAPI usa `Depends()` como valor por defecto en argumentos de función. Esta regla choca con el diseño de FastAPI, por eso la desactivamos.

### 2.3. Uso para Desarrolladores

```bash
# Verificar errores (solo lectura)
ruff check .

# Verificar y corregir automáticamente lo que sea posible (Recomendado)
ruff check --fix .

# Formatear código (Reescribir archivos)
ruff format .
```

---

## 3. MyPy (Tipado Estático)

[MyPy](https://mypy.readthedocs.io/) es un verificador de tipos estático. Python es dinámico, pero con "Type Hints" (pistas de tipo) y MyPy, podemos validar la corrección del código sin ejecutarlo.

### 3.1. ¿Para qué se usa?
Para asegurar que si una función espera un `int`, no le pases un `str`. Esto previene `TypeError` en producción.

### 3.2. Configuración (`mypy.ini`)

*   **Plugin Pydantic**: `plugins = pydantic.mypy`.
    *   *Crucial*: Permite a MyPy entender los modelos de Pydantic y SQLModel, que usan mucha metaprogramación y validación en tiempo de ejecución.
*   **Ignore Missing Imports**: `True`. Evita errores si usamos librerías externas que no tienen tipos definidos.
*   **Strictness**:
    *   `warn_return_any`: Avisa si una función devuelve `Any` cuando debería devolver algo específico.
    *   `warn_unused_configs`: Avisa si hay configuración basura en el archivo.

### 3.3. Uso para Desarrolladores

```bash
mypy .
```

**Nota**: Si ves errores de `import`, a veces es necesario crear un archivo `__init__.py` en carpetas de scripts para que MyPy las trate como módulos.

#### Tipado de SQLModel
SQLModel combina SQLAlchemy y Pydantic. A veces MyPy se confunde con las consultas.
*   **Convención**: Si MyPy se queja de algo que sabes que es correcto (ej. `AuditLog.timestamp.desc()`), puedes usar `# type: ignore` al final de la línea, pero úsalo con moderación.

---

## 4. Flujo de Trabajo Recomendado

Antes de hacer `git commit`, ejecuta siempre:

```bash
# 1. Corrige imports y errores simples
./env/bin/ruff check --fix .

# 2. Formatea el código bonito
./env/bin/ruff format .

# 3. Verifica tipos estrictos
./env/bin/mypy .
```

Si todo pasa en verde ("All checks passed", "Success"), tu código está listo para revisión.

---

## 5. Recursos Adicionales

*   [Reglas de Ruff](https://docs.astral.sh/ruff/rules/): Lista completa de qué significa cada código (E501, F401, etc.).
*   [FastAPI & MyPy](https://fastapi.tiangolo.com/python-types/): Guía oficial de FastAPI sobre tipos.
*   [Pydantic Plugin for MyPy](https://docs.pydantic.dev/latest/integrations/mypy/): Detalles sobre la integración de tipos.
