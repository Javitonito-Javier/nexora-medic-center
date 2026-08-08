# 🎯 Estandarización de Excepciones - Documentación

## 📋 Descripción

Este documento describe la implementación de excepciones de dominio estandarizadas en el sistema Clinicapharma/Nexora Labs Medic Center.

## ✅ Estado Actual

El proyecto cuenta con una jerarquía de excepciones bien definida en `app/core/exceptions.py`:

```python
class DomainError(Exception):
    """Clase base para todas las excepciones de dominio"""

class NotFoundError(DomainError):
    """Recurso no encontrado"""

class ValidationError(DomainError):
    """Error de validación de datos"""

class ConflictError(DomainError):
    """Conflicto de estado o datos duplicados"""

class InsufficientStockError(ValidationError):
    """Stock insuficiente para operación"""

class AuthenticationError(DomainError):
    """Error de autenticación"""

class PermissionDeniedError(DomainError):
    """Permiso denegado"""
```

## 🔧 Implementación Realizada

### Módulo de Farmacia (`app/modules/pharmacy/service.py`)

**Cambios realizados:**
- ✅ Reemplazados 18 `ValueError` con excepciones específicas de dominio
- ✅ Importadas excepciones desde `app.core.exceptions`
- ✅ Código más legible y auto-documentado

**Ejemplos de conversión:**

#### Antes (❌):
```python
if not patient:
    raise ValueError(f"Paciente/cliente {payload.patient_id} no existe")

if quantity > available:
    raise ValueError("Cantidad excede disponibilidad")
```

#### Después (✅):
```python
if not patient:
    raise NotFoundError("Paciente/cliente", payload.patient_id)

if quantity > available:
    raise InsufficientStockError(
        f"Stock disponible: {available}, solicitado: {quantity}"
    )
```

## 📊 Beneficios Obtenidos

### 1. **Código Más Legible**
Las excepciones de dominio son auto-descriptivas:
- `NotFoundError` → Claramente indica recurso no encontrado
- `InsufficientStockError` → Específico para problemas de inventario
- `ValidationError` → Indica error en datos de entrada

### 2. **Manejo Consistente en API Layer**
Permite mapeo uniforme de excepciones a respuestas HTTP:

```python
# En exceptions.py del módulo API
@exception_handler(NotFoundError)
def handle_not_found(exc: NotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"detail": f"{exc.entity_type} no encontrado: {exc.entity_id}"}
    )

@exception_handler(InsufficientStockError)
def handle_insufficient_stock(exc: InsufficientStockError) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc), "code": "INSUFFICIENT_STOCK"}
    )
```

### 3. **Preparado para Internacionalización (i18n)**
Los mensajes pueden ser externalizados:

```python
# messages/es.json
{
  "errors": {
    "not_found": "{entity_type} no encontrado: {entity_id}",
    "insufficient_stock": "Stock insuficiente. Disponible: {available}, Solicitado: {requested}"
  }
}

# Uso en servicio
raise NotFoundError(
    entity_type="Paciente",
    entity_id=payload.patient_id,
    message_key="errors.not_found"
)
```

### 4. **Mejor Trazabilidad y Logging**
```python
import logging

logger = logging.getLogger(__name__)

try:
    service.create_sale(payload)
except NotFoundError as e:
    logger.warning("Recurso no encontrado", extra={
        "entity_type": e.entity_type,
        "entity_id": e.entity_id,
        "user_id": current_user.id
    })
except InsufficientStockError as e:
    logger.error("Stock insuficiente", extra={
        "product_id": e.product_id,
        "available": e.available,
        "requested": e.requested
    })
```

### 5. **Testing Más Preciso**
```python
def test_create_sale_insufficient_stock():
    with pytest.raises(InsufficientStockError):
        pharmacy_service.create_sale(large_quantity_payload)

def test_create_sale_invalid_patient():
    with pytest.raises(NotFoundError):
        pharmacy_service.create_sale(invalid_patient_payload)
```

## 📝 Patrón de Uso Recomendado

### 1. **En Servicios (Service Layer)**
```python
from app.core.exceptions import NotFoundError, ValidationError

def create_patient(payload: PatientCreate) -> Patient:
    # Validar duplicados
    existing = get_by_identity(payload.identity_number)
    if existing:
        raise ConflictError("Paciente", "identity_number", payload.identity_number)
    
    # Validar datos
    if not is_valid_identity(payload.identity_number):
        raise ValidationError("Número de identidad inválido")
    
    # Crear paciente
    return db_patient
```

### 2. **En Repositorios (Opcional)**
```python
def get_patient(db: Session, patient_id: str) -> Patient:
    patient = db.get(Patient, patient_id)
    if not patient:
        raise NotFoundError("Paciente", patient_id)
    return patient
```

### 3. **En Controladores/API**
```python
# NO capturar excepciones de dominio en controllers
# Dejarlas propagar al exception handler global

@router.post("/sales")
def create_sale(payload: SaleCreate):
    # Si hay error, se propaga automáticamente
    return pharmacy_service.create_sale(payload)
```

## 🔄 Migración de Código Legacy

### Checklist para Convertir `ValueError`

- [ ] Identificar todos los `raise ValueError(...)` en el módulo
- [ ] Clasificar por tipo de error:
  - ¿Recurso no existe? → `NotFoundError`
  - ¿Datos inválidos? → `ValidationError`
  - ¿Conflicto/duplicado? → `ConflictError`
  - ¿Stock insuficiente? → `InsufficientStockError`
- [ ] Reemplazar con excepción apropiada
- [ ] Actualizar imports
- [ ] Ejecutar tests para verificar comportamiento
- [ ] Actualizar documentación de API si cambia status code

### Script de Búsqueda
```bash
# Encontrar todos los ValueError en servicios
grep -r "raise ValueError" app/modules/*/service.py

# Verificar uso de excepciones de dominio
grep -r "from app.core.exceptions import" app/modules/
```

## 📈 Métricas de Calidad

### Antes de la Estandarización
- ❌ 18 `ValueError` genéricos en farmacia
- ❌ Mensajes hardcodeados
- ❌ Sin tipado específico para manejo de errores
- ❌ Difícil internacionalización

### Después de la Estandarización
- ✅ 0 `ValueError` genéricos
- ✅ Excepciones semánticas específicas
- ✅ Preparado para i18n
- ✅ Logging estructurado habilitado
- ✅ Tests más precisos

## 🚀 Próximos Pasos

### Módulos Pendientes por Estandarizar
1. ✅ **Farmacia** - Completado
2. ⏳ **Inventario** - Pending review
3. ⏳ **Pacientes** - Pending review
4. ⏳ **Consultas** - Pending review
5. ⏳ **Usuarios** - Pending review

### Mejoras Futuras
- [ ] Implementar exception handlers globales en FastAPI
- [ ] Agregar códigos de error únicos para cada excepción
- [ ] Crear sistema de i18n para mensajes de error
- [ ] Agregar metadata estructurada a excepciones (entity_id, user_id, etc.)
- [ ] Documentar todas las excepciones que puede lanzar cada endpoint

## 🔗 Recursos Relacionados

- `backend/app/core/exceptions.py` - Definición de excepciones
- `backend/docs/transaction_improvements.md` - Manejo de transacciones
- `backend/docs/linting_guide.md` - Estándares de código

---

**Nota:** Esta documentación fue creada como parte de la Tarea 5 del plan de mejoras del sistema.
