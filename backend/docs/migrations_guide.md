# 🗄️ Guía de Migraciones de Base de Datos con Alembic

## 📋 Descripción

Este documento explica cómo usar Alembic para gestionar las migraciones de base de datos en el proyecto Clinicapharma/Nexora Labs Medic Center.

## ✅ Estado Actual

El proyecto **YA TIENE** Alembic configurado correctamente:

- ✅ `alembic.ini` - Configuración principal
- ✅ `alembic/env.py` - Entorno de migración configurado con todos los modelos
- ✅ `alembic/versions/` - Directorio con migraciones existentes
  - `faa6b0a39848_initial_baseline.py` - Línea base inicial
  - `20260623_current_schema.py` - Schema actual completo

> **Nota:** Para verificar el estado de las migraciones, necesitas tener la base de datos PostgreSQL ejecutándose. Ejecuta `alembic current` cuando el servidor esté disponible.

## 🚀 Flujo de Trabajo Recomendado

### 1. Crear una Nueva Migración

Cuando modifiques un modelo (ej. agregar columna, tabla, etc.):

```bash
cd /workspace/backend

# Generar migración automática basada en cambios en los modelos
alembic revision --autogenerate -m "descripcion_corta_del_cambio"
```

**Ejemplo:**
```bash
alembic revision --autogenerate -m "add_email_column_to_patients"
```

### 2. Revisar la Migración Generada

Alembic creará un archivo en `alembic/versions/`. **REVÍSALO SIEMPRE** antes de aplicar:

```bash
# Ver el último archivo generado
ls -lt alembic/versions/ | head -5
```

Asegúrate de que:
- ✅ Las operaciones `upgrade()` sean correctas
- ✅ Las operaciones `downgrade()` tengan sentido
- ✅ No haya operaciones no deseadas

### 3. Aplicar la Migración

```bash
# Aplicar todas las migraciones pendientes
alembic upgrade head
```

### 4. Verificar Estado

```bash
# Ver estado actual de migraciones
alembic current

# Ver historial completo
alembic history
```

## 🔄 Comandos Útiles

| Comando | Descripción |
|---------|-------------|
| `alembic current` | Muestra la versión actual de la BD |
| `alembic history` | Muestra el historial de migraciones |
| `alembic heads` | Muestra las cabezas activas |
| `alembic upgrade head` | Aplica todas las migraciones pendientes |
| `alembic downgrade -1` | Revierte la última migración |
| `alembic downgrade <revision>` | Revierte hasta una revisión específica |
| `alembic stamp head` | Marca la BD como en la versión actual sin ejecutar migraciones |

## ⚠️ Consideraciones Importantes

### 1. **NO USAR `init_db.py` para Cambios de Schema**

El archivo `app/db/init_db.py` contiene funciones `_ensure_*_columns()` que son **LEGACY**. 

**Problemas:**
- ❌ Usa SQL crudo (`ALTER TABLE`) en lugar de migraciones versionadas
- ❌ No permite rollback controlado
- ❌ Causa drift entre entornos (dev, staging, production)
- ❌ No hay registro de qué cambios se aplicaron y cuándo

**Solución:**
- ✅ Usar Alembic para TODOS los cambios de schema
- ✅ Mantener `init_db.py` solo para seed data inicial (usuario admin por defecto)

### 2. **Migraciones en Producción**

Antes de desplegar a producción:

```bash
# 1. Hacer backup de la BD
pg_dump -U usuario clinicapharma > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Probar migración en staging primero
alembic upgrade head

# 3. Verificar que todo funcione
# 4. Aplicar en producción
```

### 3. **Conflictos de Migraciones**

Si dos desarrolladores crean migraciones al mismo tiempo:

1. Fusionar manualmente los archivos de migración
2. Asegurar que `down_revision` apunte a la migración correcta
3. Probar en un entorno limpio

## 🛠️ Solución de Problemas

### Error: "Target database is not up to date"

```bash
# Ver qué migraciones faltan
alembic history

# Aplicar migraciones faltantes
alembic upgrade head
```

### Error: "Can't locate revision"

```bash
# Verificar estado actual
alembic current

# Si hay inconsistencia, marcar como actual sin ejecutar
alembic stamp head
```

### Migración Fallida

```bash
# Revertir última migración
alembic downgrade -1

# Corregir el archivo de migración
# Volver a aplicar
alembic upgrade head
```

## 📝 Ejemplo de Migración Manual

Si necesitas crear una migración manual (no automática):

```bash
alembic revision -m "manual_migration_description"
```

Editar el archivo generado:

```python
"""manual migration description

Revision ID: abc123
Revises: def456
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'abc123'
down_revision = 'def456'

def upgrade():
    op.add_column('patients', sa.Column('email', sa.String(120), nullable=True))
    op.create_index('ix_patients_email', 'patients', ['email'])

def downgrade():
    op.drop_index('ix_patients_email', table_name='patients')
    op.drop_column('patients', 'email')
```

## 🔗 Recursos Adicionales

- [Documentación Oficial de Alembic](https://alembic.sqlalchemy.org/)
- [Tutorial de Alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [Best Practices](https://alembic.sqlalchemy.org/en/latest/batch.html)

---

**Nota:** Esta guía fue creada como parte de la Tarea 9 del plan de mejoras del sistema.
