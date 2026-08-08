# 🤖 Contexto del Proyecto para IAs (AI Context)

Este documento sirve como "prompt de sistema" para cualquier asistente de IA (como GitHub Copilot, Cursor, o LLMs locales) que vaya a trabajar en el código base de **Nexora Labs Medic Center**. Su objetivo es alinear las sugerencias de código con la arquitectura y filosofía del proyecto.

---

## 📋 Información General del Proyecto
- **Nombre:** Nexora Labs Medic Center (anteriormente Clinicapharma).
- **Propósito:** Sistema de gestión clínica "Enterprise-Lite" para clínicas en crecimiento.
- **Filosofía de Diseño:** "Simplicidad Inteligente". El sistema debe ser extremadamente simple para clínicas unipersonales, pero robusto y escalable para múltiples especialistas sin cambiar de código base.
- **Estado Actual:** Producción (v2.0). Listo para despliegue con Docker.

## 🛠️ Stack Tecnológico

### Backend
- **Lenguaje:** Python 3.10+
- **Framework:** FastAPI (Async).
- **ORM:** SQLAlchemy 2.0 (Estilo moderno, `select()`, no queries antiguos).
- **Validación:** Pydantic v2 (`model_validate`, `model_dump`).
- **Base de Datos:** PostgreSQL 14+.
- **Migraciones:** Alembic.
- **Estilo de Código:** Ruff estricto (ver `ruff.toml`). Type hints obligatorios.

### Frontend
- **Framework:** Flutter 3.x (Dart).
- **Gestión de Estado:** Riverpod / Provider (según implementación actual).
- **Arquitectura:** Limpia (Controllers -> Services -> Widgets).
- **Almacenamiento Local:** Hive (para modo offline y borradores).

### Infraestructura
- **Contenerización:** Docker & Docker Compose.
- **Servidor Web:** Nginx (Proxy inverso y SSL).
- **CI/CD:** GitHub Actions (Validación de tests y linting).

## 🏛️ Reglas de Arquitectura y Negocio

### 1. Integridad de Datos Médicos (Crítico)
- **Transacciones Atómicas:** Toda operación que escriba en DB (Consultas, Ventas, Movimientos) DEBE usar el decorador `@transactional`. Nunca hagas `db.commit()` manual en los servicios.
- **Soft Deletes:** Los modelos críticos (`Patient`, `Product`, `Sale`) heredan de `SoftDeleteModel`. Nunca uses `.delete()` directo; usa `.update(is_deleted=True)`.
- **Auditoría:** Todo cambio importante debe generar un evento en el `EventService`. No modifiques datos silenciosamente.

### 2. Seguridad y Privacidad
- **RBAC Dinámico:** Los permisos se calculan en tiempo real según los roles activos. No hardcodees checks de `if user.role == 'admin'`. Usa dependencias de FastAPI `Depends(get_current_user)` y validadores de rol.
- **Datos Sensibles:** Nunca loguees contraseñas, tokens completos o datos médicos sensibles en texto plano. Usa logs estructurados.
- **Auto-Lock:** El frontend debe respetar los tiempos de inactividad. No sugieras eliminar el temporizador de bloqueo.

### 3. Experiencia de Usuario (UX) Clínica
- **Velocidad ante todo:** En el POS y Recepción, prioriza atajos de teclado y búsquedas tolerantes a errores (Fuzzy Search).
- **Offline-First:** El frontend debe guardar borradores locales (`Hive`) antes de intentar sincronizar. Si falla la red, la UI debe seguir funcionando.
- **Feedback Visual:** Usa colores semánticos (Rojo = Alergia/Peligro, Amarillo = Precaución/Vencimiento, Verde = OK).

### 4. Escalabilidad Futura
- **Modularidad:** El código está separado por módulos (`users`, `patients`, `inventory`, `pharmacy`). No crees importaciones circulares entre ellos.
- **Derivaciones:** Considera siempre que un paciente puede ser derivado entre doctores. Las consultas no son islas aisladas.

## 🚫 Patrones Prohibidos (Anti-Patrones)
- ❌ **No usar** `input()` o `print()` para depuración en producción. Usa `logger.info()`.
- ❌ **No usar** consultas SQL crudas (`text("SELECT...")`) a menos que sea estrictamente necesario y esté justificado.
- ❌ **No eliminar** registros físicos de tablas de transacciones (`Sales`, `Consultations`).
- ❌ **No asumir** que hay internet. El frontend debe manejar estados de desconexión gracefully.
- ❌ **No hardcodear** URLs o credenciales. Todo debe venir de `settings` (variables de entorno).

## 📁 Estructura de Directorios Clave
```
/backend
  /app
    /core          # Configuración, seguridad, middlewares
    /modules       # Módulos de negocio (Users, Patients, etc.)
    /api           # Rutas y endpoints
    /services      # Lógica de negocio transversal
/frontend
  /lib
    /modules       # Pantallas porfeature
    /services      # API clients y lógica offline
    /widgets       # Componentes reutilizables
/docs            # Documentación viva (Manuales, Guías Técnicas)
```

## ✅ Checklist para Generar Código Nuevo
Cuando se te pida crear una nueva feature:
1. ¿Usa type hints en todas las funciones?
2. ¿Está protegida por transacción si escribe en DB?
3. ¿Maneja errores con excepciones de dominio (`NotFoundError`, `ValidationError`)?
4. ¿Es compatible con el modo offline (si es frontend)?
5. ¿Incluye docstrings explicando el "porqué" del negocio?

---
*Si tienes dudas sobre una regla, prioriza siempre la seguridad del dato médico sobre la conveniencia del código.*
