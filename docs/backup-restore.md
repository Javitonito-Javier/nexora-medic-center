# Clinicapharma - Backup y restauracion local

Ultima revision: 2026-06-22

Este documento es obligatorio para entrega local. El cliente debe tener una rutina clara para respaldar y restaurar PostgreSQL sin depender de internet.

## Objetivo

- Crear backups diarios de la base `clinicapharma`.
- Guardar archivos verificables con SHA256.
- Poder restaurar en una base limpia si falla el equipo o se corrompen datos.

## Archivos

- Script de backup: `scripts/backup-db.ps1`
- Script de restauracion: `scripts/restore-db.ps1`
- Carpeta recomendada: `C:\ClinicapharmaBackups`
- Formato generado: `.dump` de PostgreSQL en formato custom.
- Archivo de verificacion: `.dump.sha256`

## Requisitos

- PostgreSQL instalado.
- Herramientas disponibles: `pg_dump`, `pg_restore`, `psql`.
- Usuario PostgreSQL con permisos para leer/restaurar la base.
- Password correcto de PostgreSQL.

Si PostgreSQL no esta en `PATH`, usar `-PgBin`, por ejemplo:

```powershell
-PgBin "C:\Program Files\PostgreSQL\18\bin"
```

## Backup manual

Ejecutar en PowerShell:

```powershell
cd C:\dev\clinicapharma
.\scripts\backup-db.ps1 `
  -BackupDir "C:\ClinicapharmaBackups" `
  -DbName "clinicapharma" `
  -DbUser "postgres" `
  -DbPassword "toor" `
  -DbHost "localhost" `
  -DbPort 5432
```

Resultado esperado:

- Archivo `clinicapharma_YYYY-MM-DD_HHMMSS.dump`.
- Archivo `clinicapharma_YYYY-MM-DD_HHMMSS.dump.sha256`.
- Linea nueva en `C:\ClinicapharmaBackups\backup.log`.

## Backup con PostgreSQL fuera del PATH

```powershell
cd C:\dev\clinicapharma
.\scripts\backup-db.ps1 `
  -DbPassword "toor" `
  -PgBin "C:\Program Files\PostgreSQL\18\bin"
```

## Restauracion

La restauracion reemplaza la base destino. El script exige `-ConfirmRestore` para evitar accidentes.

1. Cerrar el backend y cualquier programa conectado a la base.
2. Verificar que existe el backup.
3. Ejecutar:

```powershell
cd C:\dev\clinicapharma
.\scripts\restore-db.ps1 `
  -BackupFile "C:\ClinicapharmaBackups\clinicapharma_2026-06-22_153000.dump" `
  -ConfirmRestore `
  -DbName "clinicapharma" `
  -DbUser "postgres" `
  -DbPassword "toor" `
  -DbHost "localhost" `
  -DbPort 5432
```

Si existe `.sha256`, el script valida el hash antes de restaurar.

## Verificacion despues de restaurar

1. Iniciar backend.
2. Abrir `http://127.0.0.1:8000/health`.
3. Entrar al sistema.
4. Revisar pacientes, inventario, ventas y recibos recientes.
5. Crear un backup nuevo luego de confirmar que todo esta correcto.

## Prueba realizada

Fecha: 2026-06-22.

- Backup real generado desde `clinicapharma`.
- Restauracion probada en base temporal `clinicapharma_restore_test`.
- Base temporal eliminada despues de validar restauracion.

## Rutina recomendada para cliente

- Backup diario al cierre de operaciones.
- Copia semanal a memoria USB o disco externo.
- Conservar minimo 30 dias.
- Probar restauracion antes de entrega y luego una vez al mes.

## Riesgos y cuidados

- No guardar backups solo en la misma computadora si es posible evitarlo.
- No restaurar sin estar seguro del archivo elegido.
- No borrar `.sha256`; ayuda a detectar corrupcion.
- No compartir password de PostgreSQL con personal no autorizado.
