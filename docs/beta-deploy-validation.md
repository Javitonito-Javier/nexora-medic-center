# Clinicapharma - Validacion beta local

Ultima revision: 2026-07-12

## Validacion 2026-07-12 (paquete regenerado con rediseño y fuente local)

Paquete regenerado con `build-local-release.ps1` incluyendo rediseño de sidebar/tema, fuente Manrope local y reportes avanzados.

Ambiente probado:

- API en `http://127.0.0.1:8000`, frontend en `http://127.0.0.1:8080`.
- Base de datos limpia `clinicapharma_smoke` (equivalente a instalacion nueva).
- `.env` con `SECRET_KEY` e `INITIAL_ADMIN_PASSWORD` generados fuertes.
- Venv del paquete creado desde cero por `start-local.ps1` (valida instalacion de dependencias en frio).

Resultados:

- `start-local.ps1` creo venv, instalo dependencias, aplico migraciones Alembic (baseline + esquema actual) y arranco API y web.
- Smoke test: health OK, login admin OK, `GET /reports/summary` 200, `GET /reports/sales` 200, frontend 200 con titulo Clinicapharma, fuente Manrope servida en `/assets/assets/fonts/` 200.

Bugs encontrados y corregidos durante esta validacion:

1. `start-local.ps1` y `build-local-release.ps1` morian en PowerShell 5.1 cuando pip escribia warnings a stderr (`$ErrorActionPreference = "Stop"` + NativeCommandError). Corregido con helper `Invoke-Native` que valida solo el codigo de salida.
2. El login del admin sembrado devolvia 500 en instalacion limpia: `init_db` otorga el permiso `audit` pero el Literal `StaffModule` de `backend/app/modules/users/schemas.py` no lo incluia, y la validacion de `LoginResponse` fallaba. Corregido agregando `"audit"` al Literal, con test de regresion en `tests/test_users.py`.

## Resultado

Beta local sin factura SAR real: apta para prueba piloto controlada.

Porcentaje estimado despues de esta validacion:

- Deploy beta local sin SAR real: 93%.
- Entrega local final sin SAR real: 82%.
- Entrega con factura SAR real completa: 62%.

## Ambiente probado

- Paquete: `release/clinicapharma-local`.
- API probada en: `http://127.0.0.1:8010`.
- Frontend probado en: `http://127.0.0.1:8090`.
- Motivo de puertos alternos: el puerto `8000` tenia una instancia local previa/stale durante la prueba.

## Validaciones ejecutadas

- `build-local-release.ps1` genero paquete local.
- `start-local.ps1` arranco API y frontend estatico desde el paquete.
- `health-check.ps1` paso:
  - API health.
  - Configuracion publica de negocio.
  - Frontend estatico.
- Smoke test funcional contra el paquete:
  - Login admin.
  - Creacion de paciente beta.
  - Upload multipart de adjunto PDF como evidencia de descuento.
- `stop-local.ps1` detuvo procesos del paquete.
- Scripts de servicios Windows preparados:
  - `install-local-services.ps1`
  - `uninstall-local-services.ps1`
- Guard de seguridad en arranque:
  - Bloquea `SECRET_KEY` vacio/default.
  - Bloquea `INITIAL_ADMIN_PASSWORD` vacio/default.

## Validaciones tecnicas relacionadas

- Backend: `ruff check app tests alembic` OK.
- Backend: `pytest` OK, 23 tests.
- Frontend: `flutter analyze` OK.
- Build web: OK desde script de release.
- PowerShell syntax check de scripts de deploy: OK para build, start, stop, health-check, install-services y uninstall-services.

## Pendiente para 100% beta

- Probar el mismo paquete en una computadora limpia o VM.
- Instalar NSSM y validar que `ClinicapharmaAPI` y `ClinicapharmaWeb` arrancan automaticamente tras reiniciar.
- Probar impresora real y papel 58mm/80mm.
- Validar flujo manual completo con usuario real:
  login, paciente, cita, consulta, receta, cobro, venta farmacia, inventario, adjunto, caja, reporte y auditoria.
- Confirmar que la beta opera solo con recibos internos si SAR no estara listo.

## Nota servicios Windows

Los scripts de instalacion de servicios quedan listos, pero no se marcaron como validados porque NSSM no esta instalado en el entorno local de desarrollo. Deben probarse en la computadora destino o una VM Windows limpia.

## Nota SAR

No activar factura SAR real en beta hasta completar `sar-compliance-roadmap.md` y validar con contador/cliente.
