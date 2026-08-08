# Clinicapharma - Deploy local Windows

Ultima revision: 2026-06-24

Esta guia deja un paquete local reproducible para una computadora servidor Windows. El modo recomendado para entrega sin SAR real es operar con recibos internos.

## 1. Preparar equipo

Instalar:

- Git for Windows.
- Python 3.11 o 3.12.
- PostgreSQL 18 o compatible.
- Flutter SDK solo si se va a compilar en el equipo tecnico.

Crear base:

```sql
CREATE DATABASE clinicapharma;
```

## 2. Crear paquete local

Desde el repo:

```powershell
cd C:\dev\clinicapharma
.\scripts\build-local-release.ps1 -ApiBaseUrl "http://127.0.0.1:8000/api/v1"
```

Salida esperada:

```text
release\clinicapharma-local
```

## 3. Configurar `.env`

En el paquete:

```powershell
cd C:\dev\clinicapharma\release\clinicapharma-local
Copy-Item .\backend\.env.example .\backend\.env
notepad .\backend\.env
```

Cambiar como minimo:

- `DATABASE_URL`
- `SECRET_KEY`
- `INITIAL_ADMIN_PASSWORD`
- `ATTACHMENT_STORAGE_DIR`

`start-local.ps1` e `install-local-services.ps1` no arrancan si `SECRET_KEY` o `INITIAL_ADMIN_PASSWORD` conservan valores de ejemplo.

## 4. Arrancar sistema

```powershell
cd C:\dev\clinicapharma\release\clinicapharma-local
.\scripts\start-local.ps1
```

Abrir:

- Frontend: `http://127.0.0.1:8080`
- API health: `http://127.0.0.1:8000/health`
- API docs: `http://127.0.0.1:8000/docs`

## 5. Verificar

```powershell
.\scripts\health-check.ps1
```

Debe mostrar `OK` en API, configuracion publica y frontend.

## 6. Parar sistema

```powershell
.\scripts\stop-local.ps1
```

## 7. Instalar servicios Windows

Requiere NSSM instalado y PowerShell como administrador.

```powershell
cd C:\dev\clinicapharma\release\clinicapharma-local
.\scripts\install-local-services.ps1
.\scripts\health-check.ps1
```

Servicios creados:

- `ClinicapharmaAPI`
- `ClinicapharmaWeb`

Para desinstalar:

```powershell
.\scripts\uninstall-local-services.ps1
```

## 8. Backup operativo

Usar:

```powershell
.\scripts\backup-db.ps1 -DbPassword "PASSWORD_POSTGRES"
```

Los adjuntos viven en `ATTACHMENT_STORAGE_DIR`; incluir esa carpeta en respaldos operativos.

## 9. Checklist de entrega

- Backend inicia sin consola interactiva.
- Frontend abre en navegador local.
- Login con admin temporal funciona.
- Se crea paciente.
- Se agenda cita.
- Se registra consulta.
- Se crea receta.
- Se cobra recibo clinico.
- Se hace venta farmacia.
- Se sube adjunto al expediente.
- Se abre/cierra caja.
- Se revisa reporte y auditoria.
- Backup genera `.dump` y `.sha256`.
