param(
    [string]$ReleaseDir = (Join-Path $PSScriptRoot "..\release\clinicapharma-local"),
    [string]$ApiBaseUrl = "http://127.0.0.1:8000/api/v1",
    [switch]$SkipBackendInstall
)

$ErrorActionPreference = "Stop"

function Invoke-Native {
    param(
        [scriptblock]$Command,
        [string]$Description
    )
    # PowerShell 5.1 con ErrorActionPreference=Stop convierte cualquier linea de
    # stderr de un ejecutable nativo (p. ej. warnings de pip) en error fatal.
    # Se ejecuta con preferencia Continue y se valida solo el codigo de salida.
    $previousPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        & $Command 2>&1 | ForEach-Object { "$_" } | Write-Output
        $exitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousPreference
    }
    if ($exitCode -ne 0) {
        throw "$Description fallo con codigo de salida $exitCode."
    }
}

$rootDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$backendDir = Join-Path $rootDir "backend"
$frontendDir = Join-Path $rootDir "frontend"
$releaseDirResolved = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($ReleaseDir)

Write-Output "Building Clinicapharma local release..."
Write-Output "Root: $rootDir"
Write-Output "Release: $releaseDirResolved"

if (-not $SkipBackendInstall) {
    Push-Location $backendDir
    try {
        if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
            Invoke-Native -Command { python -m venv .venv } -Description "Creacion de entorno virtual"
        }
        Invoke-Native -Command { & ".\.venv\Scripts\python.exe" -m pip install -e ".[dev]" } -Description "Instalacion de dependencias backend"
        Invoke-Native -Command { & ".\.venv\Scripts\python.exe" -m alembic upgrade head } -Description "Migracion de base de datos"
    }
    finally {
        Pop-Location
    }
}

Push-Location $frontendDir
try {
    flutter pub get
    flutter build web --no-wasm-dry-run --dart-define=API_BASE_URL=$ApiBaseUrl
}
finally {
    Pop-Location
}

if (Test-Path -LiteralPath $releaseDirResolved) {
    Remove-Item -LiteralPath $releaseDirResolved -Recurse -Force
}

New-Item -ItemType Directory -Path $releaseDirResolved -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $releaseDirResolved "backend") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $releaseDirResolved "frontend") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $releaseDirResolved "scripts") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $releaseDirResolved "local_data\attachments") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $releaseDirResolved "logs") -Force | Out-Null

Copy-Item -Path (Join-Path $backendDir "app") -Destination (Join-Path $releaseDirResolved "backend\app") -Recurse
Copy-Item -Path (Join-Path $backendDir "alembic") -Destination (Join-Path $releaseDirResolved "backend\alembic") -Recurse
Copy-Item -Path (Join-Path $backendDir "alembic.ini") -Destination (Join-Path $releaseDirResolved "backend\alembic.ini")
Copy-Item -Path (Join-Path $backendDir "pyproject.toml") -Destination (Join-Path $releaseDirResolved "backend\pyproject.toml")
Copy-Item -Path (Join-Path $backendDir ".env.example") -Destination (Join-Path $releaseDirResolved "backend\.env.example")
Copy-Item -Path (Join-Path $frontendDir "build\web\*") -Destination (Join-Path $releaseDirResolved "frontend") -Recurse
Copy-Item -Path (Join-Path $rootDir "scripts\start-local.ps1") -Destination (Join-Path $releaseDirResolved "scripts\start-local.ps1")
Copy-Item -Path (Join-Path $rootDir "scripts\stop-local.ps1") -Destination (Join-Path $releaseDirResolved "scripts\stop-local.ps1")
Copy-Item -Path (Join-Path $rootDir "scripts\health-check.ps1") -Destination (Join-Path $releaseDirResolved "scripts\health-check.ps1")
Copy-Item -Path (Join-Path $rootDir "scripts\install-local-services.ps1") -Destination (Join-Path $releaseDirResolved "scripts\install-local-services.ps1")
Copy-Item -Path (Join-Path $rootDir "scripts\uninstall-local-services.ps1") -Destination (Join-Path $releaseDirResolved "scripts\uninstall-local-services.ps1")
Copy-Item -Path (Join-Path $rootDir "scripts\backup-db.ps1") -Destination (Join-Path $releaseDirResolved "scripts\backup-db.ps1")
Copy-Item -Path (Join-Path $rootDir "scripts\restore-db.ps1") -Destination (Join-Path $releaseDirResolved "scripts\restore-db.ps1")

Write-Output "Release package ready: $releaseDirResolved"
Write-Output "Next: copy backend\.env.example to backend\.env and set DATABASE_URL, SECRET_KEY and INITIAL_ADMIN_PASSWORD."
