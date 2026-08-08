param(
    [string]$BackendDir = (Resolve-Path "$PSScriptRoot\..\backend").Path,
    [string]$ServiceName = "ClinicapharmaAPI",
    [string]$PythonExe = "python",
    [string]$Port = "8000"
)

Write-Output "Instalando servicio Windows: $ServiceName"
Write-Output "Directorio backend: $BackendDir"

$venvPython = Join-Path -Path $BackendDir -ChildPath ".venv\Scripts\python.exe"
if (Test-Path -LiteralPath $venvPython) {
    $PythonExe = $venvPython
}

$appModule = "app.main:app"
$nssmPath = "nssm"
$nssmExists = Get-Command $nssmPath -ErrorAction SilentlyContinue

if (-not $nssmExists) {
    Write-Output ""
    Write-Output "NSSM no encontrado. Instala NSSM desde https://nssm.cc/download"
    Write-Output "y asegurate de que este en PATH, o usa el script de arranque manual:"
    Write-Output ""
    Write-Output "Crea una tarea programada en Windows con:"
    Write-Output "   schtasks /CREATE /SC ONSTART /TN $ServiceName /TR `"$PythonExe -m uvicorn $appModule --host 0.0.0.0 --port $Port`" /RL HIGHEST"
    Write-Output ""
    Write-Output "O crea un acceso directo en: shell:startup"
    Write-Output "   $PythonExe -m uvicorn $appModule --host 0.0.0.0 --port $Port"
    exit 1
}

nssm install $ServiceName `
    "C:\Windows\System32\cmd.exe" `
    "/c cd /d `"$BackendDir`" && `"$PythonExe`" -m uvicorn $appModule --host 0.0.0.0 --port $Port"

nssm set $ServiceName AppDirectory $BackendDir
nssm set $ServiceName Start SERVICE_AUTO_START
nssm set $ServiceName AppStdout "$BackendDir\logs\access.log"
nssm set $ServiceName AppStderr "$BackendDir\logs\error.log"
nssm set $ServiceName AppRotateFiles 1
nssm set $ServiceName AppRotateOnline 1
nssm set $ServiceName AppRotateBytes 52428800

New-Item -ItemType Directory -Path "$BackendDir\logs" -Force | Out-Null

Write-Output "Servicio instalado. Iniciando..."
nssm start $ServiceName
Write-Output "Servicio iniciado. Verifica con: nssm status $ServiceName"
