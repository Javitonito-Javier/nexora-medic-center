param(
    [string]$RootDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,
    [int]$ApiPort = 8000,
    [int]$WebPort = 8080
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

$backendDir = Join-Path $RootDir "backend"
$frontendDir = Join-Path $RootDir "frontend"
$frontendStaticDir = $frontendDir
if (-not (Test-Path -LiteralPath (Join-Path $frontendStaticDir "index.html"))) {
    $frontendStaticDir = Join-Path $frontendDir "build\web"
}
$logsDir = Join-Path $RootDir "logs"
$apiPidFile = Join-Path $RootDir "clinicapharma-api.pid"
$webPidFile = Join-Path $RootDir "clinicapharma-web.pid"
$pythonExe = Join-Path $backendDir ".venv\Scripts\python.exe"

New-Item -ItemType Directory -Path $logsDir -Force | Out-Null

function Assert-PortAvailable {
    param([int]$Port)
    $listener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if ($listener) {
        throw "Port $Port is already in use by process $($listener.OwningProcess). Stop it or choose another port."
    }
}

function Get-EnvFileValue {
    param(
        [string]$EnvFile,
        [string]$Name
    )
    $match = Get-Content -Path $EnvFile |
        Where-Object { $_ -match "^\s*$Name\s*=" } |
        Select-Object -Last 1
    if (-not $match) {
        return ""
    }
    return ($match -replace "^\s*$Name\s*=\s*", "").Trim().Trim('"').Trim("'")
}

function Assert-SafeEnv {
    param([string]$EnvFile)

    $secretKey = Get-EnvFileValue -EnvFile $EnvFile -Name "SECRET_KEY"
    $initialPassword = Get-EnvFileValue -EnvFile $EnvFile -Name "INITIAL_ADMIN_PASSWORD"

    if ($secretKey -in @("", "change-me", "change-me-in-local-env")) {
        throw "SECRET_KEY inseguro en backend\.env. Define un secreto largo y unico antes de arrancar."
    }
    if ($initialPassword -in @("", "admin123", "change-this-before-delivery")) {
        throw "INITIAL_ADMIN_PASSWORD inseguro en backend\.env. Define una clave temporal unica antes de arrancar."
    }
}

Assert-PortAvailable -Port $ApiPort
Assert-PortAvailable -Port $WebPort

$envFile = Join-Path $backendDir ".env"
if (-not (Test-Path -LiteralPath $envFile)) {
    throw "Missing backend\.env. Copy backend\.env.example to backend\.env and configure it first."
}
Assert-SafeEnv -EnvFile $envFile

if (-not (Test-Path -LiteralPath (Join-Path $frontendStaticDir "index.html"))) {
    throw "Missing frontend build. Run scripts\build-local-release.ps1 or flutter build web first."
}

if (-not (Test-Path -LiteralPath $pythonExe)) {
    Push-Location $backendDir
    try {
        Invoke-Native -Command { python -m venv .venv } -Description "Creacion de entorno virtual"
        Invoke-Native -Command { & $pythonExe -m pip install -e . } -Description "Instalacion de dependencias backend"
    }
    finally {
        Pop-Location
    }
}

Push-Location $backendDir
try {
    Invoke-Native -Command { & $pythonExe -m alembic upgrade head } -Description "Migracion de base de datos"
}
finally {
    Pop-Location
}

$apiProcess = Start-Process `
    -FilePath $pythonExe `
    -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "$ApiPort" `
    -WorkingDirectory $backendDir `
    -RedirectStandardOutput (Join-Path $logsDir "api.out.log") `
    -RedirectStandardError (Join-Path $logsDir "api.err.log") `
    -WindowStyle Hidden `
    -PassThru

Set-Content -Path $apiPidFile -Value $apiProcess.Id

$webProcess = Start-Process `
    -FilePath $pythonExe `
    -ArgumentList "-m", "http.server", "$WebPort", "--directory", "`"$frontendStaticDir`"" `
    -WorkingDirectory $RootDir `
    -RedirectStandardOutput (Join-Path $logsDir "web.out.log") `
    -RedirectStandardError (Join-Path $logsDir "web.err.log") `
    -WindowStyle Hidden `
    -PassThru

Set-Content -Path $webPidFile -Value $webProcess.Id

Write-Output "Clinicapharma started."
Write-Output "API: http://127.0.0.1:$ApiPort/health"
Write-Output "Web: http://127.0.0.1:$WebPort"
Write-Output "Logs: $logsDir"
