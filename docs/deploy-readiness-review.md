# Clinicapharma - Revision pre-deploy

Ultima revision: 2026-06-24

## Veredicto corto

Clinicapharma esta apto para beta local controlada sin factura SAR real. Aun no esta listo para entrega final limpia sin validacion en maquina limpia, impresora real y decision SAR.

Estimacion:

- Deploy local piloto sin factura SAR real: 93% listo.
- Entrega local final sin factura SAR real: 82% listo.
- Entrega con factura SAR real completa: 62% listo hasta implementar el Sprint SAR.

## Validaciones ejecutadas

- Backend: `pytest` paso con 23 tests.
- Backend: `ruff check app tests alembic` paso sin issues.
- Base de datos: `alembic upgrade head` ejecuto baseline y migracion de esquema actual.
- Frontend: `flutter analyze` paso sin issues.
- Frontend: `flutter build web --no-wasm-dry-run` compilo correctamente.
- Paquete local: `build-local-release.ps1` genero `release/clinicapharma-local`.
- Health-check paquete local: API, business settings y frontend OK en puertos `8010/8090`.
- Smoke test paquete local: login admin, crear paciente y subir adjunto PDF OK.

## Cambios aplicados en esta revision

- `frontend/lib/core/api_config.dart`: `ApiConfig.baseUrl` ahora puede configurarse con `--dart-define=API_BASE_URL=...`.
- `frontend/lib/features/auth/auth_api.dart`: login usa `ApiConfig.baseUrl` y deja de duplicar la URL del backend.
- `backend/alembic/versions/20260623_current_schema.py`: migracion Alembic para crear el esquema actual desde metadata.
- `backend/alembic/env.py`: Alembic registra modulos recientes de auditoria y cajas.
- `backend/app/core/config.py` y `backend/app/db/init_db.py`: usuario admin inicial se configura por `.env`.
- `backend/.env.example`: documenta `INITIAL_ADMIN_USERNAME` e `INITIAL_ADMIN_PASSWORD`.
- `docs/manual_screenshots/chrome-profile/**`: removido del indice de Git; `.gitignore` ya lo excluye.

## Bloqueantes antes de deploy final

### 1. Worktree/repo todavia no esta listo para release

Quedan muchos archivos modificados y no versionados porque hay trabajo acumulado del MVP. El perfil temporal `docs/manual_screenshots/chrome-profile/**` ya fue removido del indice y queda ignorado.

Accion:

- Decidir que cambios entran a la entrega.
- Dejar un commit/tag de release o un paquete exportado reproducible.

### 2. Migraciones iniciales cerradas, pero falta probar maquina limpia

Existe migracion `20260623_current_schema` y `alembic upgrade head` corre localmente. `init_db()` aun conserva compatibilidad con bases locales previas.

Accion:

- Probar `alembic upgrade head` en una base limpia de maquina nueva.
- Probar upgrade sobre copia de base con datos del cliente/demo.
- Dejar `init_db()` para seed/admin y seguridad operativa, no como sistema principal de migracion.

### 3. Credenciales iniciales configurables

`backend/app/db/init_db.py` crea el primer usuario usando `INITIAL_ADMIN_USERNAME` e `INITIAL_ADMIN_PASSWORD`.

Accion:

- En entrega, definir password temporal unico en `.env`.
- Cambiarlo despues de crear usuario admin del cliente.

### 4. SAR no esta listo para factura real

La configuracion fiscal existe, pero el regimen completo SAR aun no esta implementado.

Accion:

- Si el cliente no emitira factura real desde el sistema: entregar en modo recibos internos.
- Si emitira factura SAR: ejecutar `sar-compliance-roadmap.md` antes de produccion fiscal.

### 5. Servicio automatico Windows pendiente de validacion

Ya existe paquete local reproducible con scripts de arranque/parada/health-check. Tambien existen scripts para instalar API y frontend como servicios Windows usando NSSM. Falta validarlos en una computadora con NSSM instalado y confirmar arranque despues de reiniciar.

Accion:

- Confirmar carpeta final del cliente.
- Instalar NSSM o definir alternativa con tarea programada.
- Instalar `ClinicapharmaAPI` y `ClinicapharmaWeb` con `install-local-services.ps1`.
- Ejecutar `health-check.ps1` despues de reiniciar.
- Variables `.env` con secreto fuerte.
- Prueba despues de reiniciar.

## Riesgos medios

### UI mantenible, pero con pantallas muy grandes

Archivos mas pesados:

- `frontend/lib/features/pharmacy/pharmacy_screen.dart`: 2631 lineas.
- `frontend/lib/features/inventory/inventory_screen.dart`: 1659 lineas.
- `frontend/lib/features/appointments/appointments_screen.dart`: 932 lineas.
- `frontend/lib/features/patients/patient_record_screen.dart`: 881 lineas.

Riesgo:

- Dificulta correcciones visuales rapidas, responsive, pruebas y cambios de flujo.

Accion:

- No bloquear deploy por esto, pero refactorizar despues en componentes por seccion: encabezado, busqueda, carrito, pago, historial, alertas y dialogs.

### Configuracion API mejorada, pero falta documentar build

Ya se centralizo `API_BASE_URL`, pero falta documentar el comando final.

Ejemplo:

```powershell
flutter build web --dart-define=API_BASE_URL=http://127.0.0.1:8000/api/v1
```

### CORS local permisivo por regex

`backend/app/core/config.py` permite `localhost` y `127.0.0.1` con cualquier puerto. Es razonable para local, pero debe cerrarse si se publica fuera de LAN.

## Arquitectura

Lo positivo:

- Separacion clara por modulos backend: routes, schemas, service, models.
- Frontend organizado por features.
- Riverpod ya centraliza estado importante.
- Auditoria, caja, inventario por lote y backup ya van en direccion correcta.

Lo que falta endurecer:

- Configuracion de deploy.
- Menos logica UI en pantallas gigantes.
- SAR completo si aplica.
- E2E/manual final en equipo limpio.

## Ruta recomendada para deploy

### Corte A - Piloto local sin factura SAR real

1. Generar `.env` de cliente con `SECRET_KEY` fuerte y `INITIAL_ADMIN_PASSWORD` temporal.
2. Ejecutar paquete local con `start-local.ps1`.
3. Ejecutar `health-check.ps1`.
4. Probar backup/restore.
5. Validar impresora/recibos.
6. Probar flujo completo: login, paciente, cita, consulta, receta, recibo, venta farmacia, inventario, adjunto, caja, reporte y auditoria.
7. Instalar backend como servicio/tarea programada antes de dejarlo como beta diaria.

### Corte B - Final con SAR

1. Completar Corte A.
2. Implementar Sprint SAR 1 y SAR 2.
3. Probar factura, reimpresion, anulacion, nota de credito y reporte fiscal.
4. Validar con contador/cliente.
5. Activar factura real solo con aprobacion.
