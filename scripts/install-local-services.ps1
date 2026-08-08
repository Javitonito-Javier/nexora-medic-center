param(
    [string]$RootDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path,
    [string]$ApiServiceName = "ClinicapharmaAPI",
    [string]$WebServiceName = "ClinicapharmaWeb",
    [int]$ApiPort = 8000,
    [int]$WebPort = 8080
)

$ErrorActionPreference = "Stop"

$nssm = Get-Command nssm -ErrorAction SilentlyContinue
if (-not $nssm) {
    throw "NSSM no esta instalado o no esta en PATH. Instala NSSM desde https://nssm.cc/download y vuelve a ejecutar este script como administrador."
}

$backendDir = Join-Path $RootDir "backend"
$frontendDir = Join-Path $RootDir "frontend"
$frontendStaticDir = $frontendDir
if (-not (Test-Path -LiteralPath (Join-Path $frontendStaticDir "index.html"))) {
    $frontendStaticDir = Join-Path $frontendDir "build\web"
}
$logsDir = Join-Path $RootDir "logs"
$pythonExe = Join-Path $backendDir ".venv\Scripts\python.exe"
$envFile = Join-Path $backendDir ".env"

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
        throw "SECRET_KEY inseguro en backend\.env. Define un secreto largo y unico antes de instalar servicios."
    }
    if ($initialPassword -in @("", "admin123", "change-this-before-delivery")) {
        throw "INITIAL_ADMIN_PASSWORD inseguro en backend\.env. Define una clave temporal unica antes de instalar servicios."
    }
}

if (-not (Test-Path -LiteralPath $pythonExe)) {
    throw "No se encontro $pythonExe. Ejecuta start-local.ps1 una vez o instala dependencias del backend."
}
if (-not (Test-Path -LiteralPath $envFile)) {
    throw "Falta backend\.env. Configuralo antes de instalar servicios."
}
Assert-SafeEnv -EnvFile $envFile
if (-not (Test-Path -LiteralPath (Join-Path $frontendStaticDir "index.html"))) {
    throw "Falta frontend compilado. Ejecuta build-local-release.ps1 primero."
}

New-Item -ItemType Directory -Path $logsDir -Force | Out-Null

& nssm install $ApiServiceName `
    "C:\Windows\System32\cmd.exe" `
    "/c cd /d `"$backendDir`" && `"$pythonExe`" -m alembic upgrade head && `"$pythonExe`" -m uvicorn app.main:app --host 0.0.0.0 --port $ApiPort"
& nssm set $ApiServiceName AppDirectory $backendDir
& nssm set $ApiServiceName Start SERVICE_AUTO_START
& nssm set $ApiServiceName AppStdout (Join-Path $logsDir "api-service.out.log")
& nssm set $ApiServiceName AppStderr (Join-Path $logsDir "api-service.err.log")
& nssm set $ApiServiceName AppRotateFiles 1
& nssm set $ApiServiceName AppRotateOnline 1
& nssm set $ApiServiceName AppRotateBytes 52428800

& nssm install $WebServiceName `
    "C:\Windows\System32\cmd.exe" `
    "/c cd /d `"$RootDir`" && `"$pythonExe`" -m http.server $WebPort --directory `"$frontendStaticDir`""
& nssm set $WebServiceName AppDirectory $RootDir
& nssm set $WebServiceName Start SERVICE_AUTO_START
& nssm set $WebServiceName AppStdout (Join-Path $logsDir "web-service.out.log")
& nssm set $WebServiceName AppStderr (Join-Path $logsDir "web-service.err.log")
& nssm set $WebServiceName AppRotateFiles 1
& nssm set $WebServiceName AppRotateOnline 1
& nssm set $WebServiceName AppRotateBytes 52428800

& nssm start $ApiServiceName
& nssm start $WebServiceName

Write-Output "Servicios instalados e iniciados:"
Write-Output "- $ApiServiceName -> http://127.0.0.1:$ApiPort/health"
Write-Output "- $WebServiceName -> http://127.0.0.1:$WebPort"
Write-Output "Ejecuta health-check.ps1 para validar."
