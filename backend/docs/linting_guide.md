# Guía de Linting y Formato de Código

## Configuración Instalada

El proyecto utiliza **Ruff** como linter y formateador principal. Ruff es un herramienta extremadamente rápida escrita en Rust que reemplaza múltiples herramientas como flake8, isort, black, y más.

## Archivos de Configuración

- `backend/ruff.toml` - Configuración completa del linter

## Comandos Útiles

### Verificar errores (sin corregir)
```bash
cd backend
ruff check app/
```

### Corregir automáticamente lo posible
```bash
cd backend
ruff check app/ --fix
```

### Corregir incluyendo fixes "inseguros"
```bash
cd backend
ruff check app/ --fix --unsafe-fixes
```

### Ver estadísticas de errores
```bash
cd backend
ruff check app/ --statistics
```

### Formatear código
```bash
cd backend
ruff format app/
```

### Verificar formato sin cambiar
```bash
cd backend
ruff format app/ --check
```

## Reglas Habilitadas

| Código | Descripción | Herramienta Original |
|--------|-------------|---------------------|
| E      | Errores pycodestyle | pycodestyle |
| W      | Advertencias pycodestyle | pycodestyle |
| F      | Errores Pyflakes | Pyflakes |
| I      | Ordenamiento de imports | isort |
| B      | Errores comunes | flake8-bugbear |
| C4     | Comprensiones optimizadas | flake8-comprehensions |
| UP     | Sintaxis moderna Python | pyupgrade |
| SIM    | Simplificación de código | flake8-simplify |
| TCH    | Type checking | flake8-type-checking |

## Reglas Ignoradas Intencionalmente

- `E501` - Líneas muy largas (manejado por el formateador)
- `B008` - Llamadas a funciones en defaults (común en FastAPI con `Depends()`)

## Integración con IDEs

### VS Code

Instala la extensión **Ruff** y agrega a tu `settings.json`:

```json
{
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.codeActionsOnSave": {
      "source.organizeImports": "explicit",
      "source.fixAll.ruff": "explicit"
    }
  },
  "ruff.lint.args": ["--config", "backend/ruff.toml"]
}
```

### PyCharm

1. Ve a `Settings > Tools > External Tools`
2. Agrega Ruff con:
   - Name: `Ruff Check`
   - Program: `ruff`
   - Arguments: `check $FilePath$ --config backend/ruff.toml`
   - Working directory: `$ProjectFileDir$`

## Pre-commit Hook (Opcional)

Crea `.pre-commit-config.yaml` en la raíz:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format
```

Instala con:
```bash
pip install pre-commit
pre-commit install
```

## Convenciones del Proyecto

### Imports

Los imports se ordenan automáticamente en este orden:
1. Librerías estándar de Python
2. Librerías de terceros
3. Módulos locales del proyecto (`app/`)

### Excepciones

Siempre usa `raise ... from err` para preservar el traceback original:

```python
# ✅ Correcto
try:
    db.commit()
except IntegrityError as err:
    db.rollback()
    raise ConflictError("Mensaje") from err

# ❌ Incorrecto
try:
    db.commit()
except IntegrityError:
    db.rollback()
    raise ConflictError("Mensaje")
```

### Type Hints

Usa type hints modernos de Python 3.10+:

```python
# ✅ Correcto
def get_user(db: Session, user_id: str) -> User | None:

# ❌ Antiguo
from typing import Optional
def get_user(db: Session, user_id: str) -> Optional[User]:
```

## Ejecutar en CI/CD

Agrega este paso en tu pipeline:

```yaml
- name: Lint with Ruff
  run: |
    cd backend
    ruff check app/
    ruff format app/ --check
```

## Recursos

- [Documentación oficial de Ruff](https://docs.astral.sh/ruff/)
- [Reglas disponibles](https://docs.astral.sh/ruff/rules/)
- [Configuración](https://docs.astral.sh/ruff/configuration/)
