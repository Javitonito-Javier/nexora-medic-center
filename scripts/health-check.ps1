param(
    [string]$ApiBaseUrl = "http://127.0.0.1:8000",
    [string]$WebBaseUrl = "http://127.0.0.1:8080"
)

$ErrorActionPreference = "Stop"

function Test-HttpOk {
    param(
        [string]$Name,
        [string]$Url
    )

    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 10
        if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 300) {
            Write-Output "OK   $Name -> $Url"
            return
        }
        throw "HTTP $($response.StatusCode)"
    }
    catch {
        Write-Output "FAIL $Name -> $Url"
        throw
    }
}

Test-HttpOk -Name "API health" -Url "$ApiBaseUrl/health"
Test-HttpOk -Name "Business settings" -Url "$ApiBaseUrl/api/v1/business/settings"
Test-HttpOk -Name "Frontend" -Url $WebBaseUrl

Write-Output "Clinicapharma health-check completed."
