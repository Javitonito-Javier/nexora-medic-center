param(
    [Parameter(Mandatory = $true)]
    [string]$BackupFile,
    [switch]$ConfirmRestore,
    [string]$DbName = "clinicapharma",
    [string]$DbUser = "postgres",
    [string]$DbPassword = "toor",
    [string]$DbHost = "localhost",
    [int]$DbPort = 5432,
    [string]$PgBin = ""
)

$ErrorActionPreference = "Stop"

function Resolve-PgTool {
    param(
        [string]$ToolName,
        [string]$PgBinPath
    )

    if ($PgBinPath) {
        $candidate = Join-Path -Path $PgBinPath -ChildPath "$ToolName.exe"
        if (Test-Path -LiteralPath $candidate) {
            return $candidate
        }
    }

    $command = Get-Command $ToolName -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    throw "No se encontro $ToolName. Agrega PostgreSQL al PATH o usa -PgBin `"C:\Program Files\PostgreSQL\18\bin`"."
}

if (-not $ConfirmRestore) {
    throw "Restaurar reemplaza la base '$DbName'. Ejecuta de nuevo con -ConfirmRestore si estas seguro."
}

if ($DbName -notmatch '^[A-Za-z0-9_-]+$') {
    throw "DbName solo puede contener letras, numeros, guion y guion bajo."
}

$resolvedBackup = Resolve-Path -LiteralPath $BackupFile -ErrorAction Stop
$backupItem = Get-Item -LiteralPath $resolvedBackup.Path
if ($backupItem.Length -le 0) {
    throw "El archivo de backup esta vacio."
}

$shaFile = "$($resolvedBackup.Path).sha256"
if (Test-Path -LiteralPath $shaFile) {
    $expected = (Get-Content -LiteralPath $shaFile -TotalCount 1).Split(" ", [System.StringSplitOptions]::RemoveEmptyEntries)[0]
    $actual = (Get-FileHash -LiteralPath $resolvedBackup.Path -Algorithm SHA256).Hash
    if ($expected -ne $actual) {
        throw "El SHA256 del backup no coincide. No se restaura para evitar datos corruptos."
    }
}

$psql = Resolve-PgTool -ToolName "psql" -PgBinPath $PgBin
$pgRestore = Resolve-PgTool -ToolName "pg_restore" -PgBinPath $PgBin

try {
    $env:PGPASSWORD = $DbPassword

    & $psql -h $DbHost -p $DbPort -U $DbUser -d "postgres" -v ON_ERROR_STOP=1 -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DbName' AND pid <> pg_backend_pid();"
    if ($LASTEXITCODE -ne 0) { throw "No se pudieron cerrar conexiones activas." }

    & $psql -h $DbHost -p $DbPort -U $DbUser -d "postgres" -v ON_ERROR_STOP=1 -c "DROP DATABASE IF EXISTS `"$DbName`";"
    if ($LASTEXITCODE -ne 0) { throw "No se pudo eliminar la base destino." }

    & $psql -h $DbHost -p $DbPort -U $DbUser -d "postgres" -v ON_ERROR_STOP=1 -c "CREATE DATABASE `"$DbName`";"
    if ($LASTEXITCODE -ne 0) { throw "No se pudo crear la base destino." }

    & $pgRestore -h $DbHost -p $DbPort -U $DbUser -d $DbName --clean --if-exists --no-owner $resolvedBackup.Path
    if ($LASTEXITCODE -ne 0) { throw "pg_restore termino con codigo $LASTEXITCODE." }

    Write-Output "Restauracion exitosa en base '$DbName' desde $($resolvedBackup.Path)."
}
catch {
    Write-Error "Restauracion FALLIDA: $($_.Exception.Message)"
    exit 1
}
finally {
    Remove-Item Env:\PGPASSWORD -ErrorAction SilentlyContinue
}
