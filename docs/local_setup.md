# Local setup

## Required tools

- Git for Windows
- PostgreSQL 18 or compatible
- Python 3.11 or 3.12
- Flutter SDK with Chrome enabled

## Environment check

Run from PowerShell:

```powershell
python --version
git --version
psql --version
flutter doctor -v
```

## PostgreSQL

Create a database for local development:

```sql
CREATE DATABASE clinicapharma;
```

Copy `backend/.env.example` to `backend/.env` and configure the environment variables:

```text
# Generar una clave secreta única para cada instalación
python -c "import secrets; print(secrets.token_urlsafe(32))"

DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/clinicapharma
SECRET_KEY=<resultado_del_comando_anterior>
INITIAL_ADMIN_USERNAME=admin
INITIAL_ADMIN_PASSWORD=<cambie_antes_de_produccion>
ATTACHMENT_STORAGE_DIR=local_data/attachments
ATTACHMENT_MAX_SIZE_BYTES=10485760
```

### Configuración de seguridad

**SECRET_KEY**: Es crítico generar una clave única y segura para cada instalación. Esta clave se usa para:
- Firmar tokens JWT
- Encriptación de sesiones
- Seguridad general de la aplicación

**Contraseñas de usuarios**: El sistema valida que las contraseñas cumplan con:
- Mínimo 8 caracteres
- Al menos una letra mayúscula
- Al menos una letra minúscula
- Al menos un número

Para delivery, cambie `INITIAL_ADMIN_PASSWORD` antes del primer inicio y actualícelo después de crear el usuario administrador del cliente.

Mantenga `ATTACHMENT_STORAGE_DIR` fuera de los respaldos de Git destinados solo al código; inclúyalo en respaldos operativos cuando preserve archivos del expediente.

## Backup y restauracion

Antes de entrega local, probar backup y restauracion.

Backup:

```powershell
cd C:\dev\clinicapharma
.\scripts\backup-db.ps1 -DbPassword "YOUR_PASSWORD"
```

Restauracion:

```powershell
cd C:\dev\clinicapharma
.\scripts\restore-db.ps1 -BackupFile "C:\ClinicapharmaBackups\clinicapharma_YYYY-MM-DD_HHMMSS.dump" -ConfirmRestore -DbPassword "YOUR_PASSWORD"
```

Guia completa: `docs/backup-restore.md`.

## Backend

```powershell
cd C:\dev\clinicapharma\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .[dev]
alembic upgrade head
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/health
```

## Frontend

```powershell
cd C:\dev\clinicapharma\frontend
flutter pub get
flutter run -d chrome
```

Production-style web build:

```powershell
cd C:\dev\clinicapharma\frontend
flutter build web --dart-define=API_BASE_URL=http://127.0.0.1:8000/api/v1
```

## Deploy local reproducible

Para crear un paquete local:

```powershell
cd C:\dev\clinicapharma
.\scripts\build-local-release.ps1 -ApiBaseUrl "http://127.0.0.1:8000/api/v1"
```

Para arrancar el paquete:

```powershell
cd C:\dev\clinicapharma\release\clinicapharma-local
.\scripts\start-local.ps1
.\scripts\health-check.ps1
```

Para parar:

```powershell
.\scripts\stop-local.ps1
```

Guia completa: `docs/deploy-local.md`.

### Servicios Windows para entrega

En el equipo destino, con NSSM instalado y PowerShell como administrador:

```powershell
cd C:\dev\clinicapharma\release\clinicapharma-local
.\scripts\install-local-services.ps1
.\scripts\health-check.ps1
```

Para removerlos:

```powershell
.\scripts\uninstall-local-services.ps1
```
