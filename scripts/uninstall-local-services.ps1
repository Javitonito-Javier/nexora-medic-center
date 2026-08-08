param(
    [string]$ApiServiceName = "ClinicapharmaAPI",
    [string]$WebServiceName = "ClinicapharmaWeb"
)

$ErrorActionPreference = "Stop"

$nssm = Get-Command nssm -ErrorAction SilentlyContinue
if (-not $nssm) {
    throw "NSSM no esta instalado o no esta en PATH."
}

foreach ($serviceName in @($ApiServiceName, $WebServiceName)) {
    $service = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
    if (-not $service) {
        Write-Output "Servicio no existe: $serviceName"
        continue
    }
    & nssm stop $serviceName
    & nssm remove $serviceName confirm
    Write-Output "Servicio eliminado: $serviceName"
}
