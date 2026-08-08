param(
    [string]$RootDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
)

$ErrorActionPreference = "Stop"

foreach ($name in @("clinicapharma-api.pid", "clinicapharma-web.pid")) {
    $pidFile = Join-Path $RootDir $name
    if (-not (Test-Path -LiteralPath $pidFile)) {
        continue
    }

    $processId = (Get-Content -LiteralPath $pidFile -Raw).Trim()
    if ($processId) {
        $process = Get-Process -Id ([int]$processId) -ErrorAction SilentlyContinue
        if ($process) {
            Stop-Process -Id $process.Id -Force
            Write-Output "Stopped $name process $processId."
        }
    }
    Remove-Item -LiteralPath $pidFile -Force
}

Write-Output "Clinicapharma local processes stopped."
