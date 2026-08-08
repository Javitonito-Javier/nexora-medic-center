param(
    [string]$BackupDir = "C:\ClinicapharmaBackups",
    [int]$RetentionDays = 30,
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

if ($RetentionDays -lt 1) {
    throw "RetentionDays debe ser mayor o igual a 1."
}

if ($DbName -notmatch '^[A-Za-z0-9_-]+$') {
    throw "DbName solo puede contener letras, numeros, guion y guion bajo."
}

$pgDump = Resolve-PgTool -ToolName "pg_dump" -PgBinPath $PgBin
$timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$backupFile = Join-Path -Path $BackupDir -ChildPath "$DbName`_$timestamp.dump"
$shaFile = "$backupFile.sha256"
$logFile = Join-Path -Path $BackupDir -ChildPath "backup.log"

if (-not (Test-Path -LiteralPath $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
}

try {
    $env:PGPASSWORD = $DbPassword
    & $pgDump -h $DbHost -p $DbPort -U $DbUser -d $DbName -F c -f $backupFile

    if ($LASTEXITCODE -ne 0) {
        throw "pg_dump termino con codigo $LASTEXITCODE."
    }

    if (-not (Test-Path -LiteralPath $backupFile)) {
        throw "No se genero el archivo de backup."
    }

    $backupItem = Get-Item -LiteralPath $backupFile
    if ($backupItem.Length -le 0) {
        throw "El archivo de backup quedo vacio."
    }

    $hash = Get-FileHash -LiteralPath $backupFile -Algorithm SHA256
    Set-Content -Path $shaFile -Value "$($hash.Hash)  $($backupItem.Name)"

    $sizeMb = [math]::Round($backupItem.Length / 1MB, 2)
    $msg = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Backup exitoso: $backupFile ($sizeMb MB)"
    Add-Content -Path $logFile -Value $msg
    Write-Output $msg

    $limit = (Get-Date).AddDays(-$RetentionDays)
    Get-ChildItem -Path $BackupDir -Filter "$DbName`_*.dump" |
        Where-Object { $_.LastWriteTime -lt $limit } |
        ForEach-Object {
            Remove-Item -LiteralPath $_.FullName -Force
            $oldHash = "$($_.FullName).sha256"
            if (Test-Path -LiteralPath $oldHash) {
                Remove-Item -LiteralPath $oldHash -Force
            }
            $cleanupMsg = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Backup antiguo eliminado: $($_.Name)"
            Add-Content -Path $logFile -Value $cleanupMsg
        }
}
catch {
    $msg = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Backup FALLIDO: $($_.Exception.Message)"
    Add-Content -Path $logFile -Value $msg
    Write-Error $msg
    exit 1
}
finally {
    Remove-Item Env:\PGPASSWORD -ErrorAction SilentlyContinue
}
