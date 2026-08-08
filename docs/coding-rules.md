# Clinicapharma - Coding Rules

Ultima revision: 2026-06-12

## Regla de documentacion

Antes de cualquier cambio futuro:

1. Leer todos los `.md` de `docs/`.
2. Tomar `docs/requirements.md` como fuente principal de verdad.
3. Si se modifica una pantalla, flujo, funcion, permiso o validacion, actualizar `docs/module-flows.md`.
4. Si se modifica base de datos, actualizar `docs/database-schema.md`.
5. Si se agrega/cambia endpoint, actualizar `docs/api-contract.md`.
6. Si se completa una tarea o cambia prioridad de entrega, marcarlo en `docs/roadmap.md`.
7. Si se agrega funcionalidad importante, actualizar `docs/changelog.md`.
8. Si hay inconsistencia entre codigo y docs, avisar y proponer correccion.
9. Ningun cambio funcional queda listo si `requirements.md`, `module-flows.md`, `api-contract.md`, `database-schema.md`, `roadmap.md` y `changelog.md` no fueron revisados.

Los PDFs, PNGs y perfiles temporales dentro de `docs/manual_screenshots` son artefactos generados; no deben tratarse como fuente de verdad.

## Backend

- Mantener arquitectura por modulo: `models.py`, `schemas.py`, `service.py`, ruta en `api/routes`.
- Usar SQLAlchemy 2 con `Mapped` y `mapped_column`.
- Mantener validaciones en schemas/servicios, no en la UI solamente.
- No duplicar reglas criticas de negocio solo en frontend.
- Ventas, puntos e inventario deben ser transaccionales.
- Toda operacion sensible debe dejar rastro en tablas de movimientos o auditoria.
- Mantener OpenAPI entendible mediante response models.

## Frontend

- Mantener feature-first en `frontend/lib/features`.
- Usar Riverpod para estado compartido y controladores.
- Usar GoRouter para rutas.
- Reutilizar tema global; no hardcodear colores fuera del sistema de tema salvo casos justificados.
- Evitar overflow en formularios; preferir scroll y layouts responsivos.
- Pantallas operativas deben priorizar velocidad y claridad.

## Base de datos

- Nuevas tablas deben tener ids estables, timestamps si aplica e indices para busquedas frecuentes.
- Inventario no debe depender solo de un stock global; debe preservar movimientos y lotes.
- Farmacia POS no debe descontar ni recomendar lotes vencidos; FEFO/FIFO solo aplica sobre existencia vigente.
- Evitar romper datos existentes; usar migraciones o compatibilidad en `init_db` mientras no exista Alembic formal.

## Pruebas recomendadas

Backend:

```powershell
cd C:\dev\clinicapharma\backend
.\.venv\Scripts\Activate.ps1
pytest
```

Frontend:

```powershell
cd C:\dev\clinicapharma\frontend
flutter analyze
flutter build web --no-wasm-dry-run
```

## Git

- No revertir cambios del usuario sin permiso.
- Mantener commits pequenos por bloque funcional.
- Antes de deploy o entrega, revisar `git status --short`.
