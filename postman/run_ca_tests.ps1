# ==============================================================================
# Script de Pruebas Automatizadas Retail 360 - Skala Evaluación (CA-01 a CA-12)
# ==============================================================================

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "    RETAIL 360 - SUITE DE PRUEBAS END-TO-END (CA-01 A CA-12)     " -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

$expUrl = "http://127.0.0.1:8081/api/v1"
$proUrl = "http://127.0.0.1:8082/internal/v1"
$results = @()

function Test-Endpoint {
    param(
        [string]$Id,
        [string]$Name,
        [string]$Method,
        [string]$Url,
        [hashtable]$Headers,
        [string]$Body,
        [int[]]$ExpectedStatus
    )

    Write-Host "`n[$Id] Ejecutando: $Name" -ForegroundColor Yellow
    Write-Host "       $Method $Url" -ForegroundColor Gray

    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    $status = 0
    $respBody = ""

    try {
        $params = @{
            Uri = $Url
            Method = $Method
            Headers = $Headers
            UseBasicParsing = $true
            TimeoutSec = 20
            ErrorAction = "Stop"
        }
        if ($Body) {
            $params["Body"] = $Body
            $params["ContentType"] = "application/json"
        }

        $response = Invoke-WebRequest @params
        $stopwatch.Stop()
        $status = [int]$response.StatusCode
        $respBody = $response.Content
    }
    catch {
        $stopwatch.Stop()
        if ($_.Exception.Response) {
            $status = [int]$_.Exception.Response.StatusCode
            $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
            $respBody = $reader.ReadToEnd()
        } else {
            $status = 0
            $respBody = $_.Exception.Message
        }
    }

    $passed = $ExpectedStatus -contains $status
    $statusColor = if ($passed) { "Green" } else { "Red" }
    $passText = if ($passed) { "PASS" } else { "FAIL" }

    Write-Host "       Resultado: $passText (Status: $status | Esperado: $($ExpectedStatus -join '/')) en $($stopwatch.ElapsedMilliseconds)ms" -ForegroundColor $statusColor
    if ($respBody.Length -gt 0) {
        $preview = if ($respBody.Length -gt 350) { $respBody.Substring(0, 350) + "..." } else { $respBody }
        Write-Host "       Cuerpo: $preview" -ForegroundColor DarkGray
    }

    return [PSCustomObject]@{
        ID = $Id
        Prueba = $Name
        Metodo = $Method
        Status = $status
        Esperado = ($ExpectedStatus -join '/')
        Resultado = $passText
        TiempoMs = $stopwatch.ElapsedMilliseconds
    }
}

# CA-01: Consultar producto existente
$results += Test-Endpoint -Id "CA-01" -Name "Consultar LAP-001 (PostgreSQL)" -Method "GET" `
    -Url "$expUrl/products/LAP-001" -Headers @{"X-Correlation-ID"="corr-ca-01"} -ExpectedStatus @(200)

# CA-02: Alta de orden exitosa sincronizada (ORD-1001)
$bodyCa02 = @'
{
  "orderId": "ORD-1001",
  "customer": {
    "customerId": "CUST-001",
    "name": "Juan Perez",
    "email": "juan.perez@example.com"
  },
  "items": [
    {"sku": "LAP-001", "quantity": 2},
    {"sku": "MOU-001", "quantity": 3}
  ]
}
'@
$results += Test-Endpoint -Id "CA-02" -Name "Alta de orden exitosa ORD-1001" -Method "POST" `
    -Url "$expUrl/orders" -Headers @{"X-Correlation-ID"="corr-ca-02"} -Body $bodyCa02 -ExpectedStatus @(201, 202, 409)

# CA-03: Consultar orden ORD-1001
$results += Test-Endpoint -Id "CA-03" -Name "Consultar orden creada ORD-1001" -Method "GET" `
    -Url "$expUrl/orders/ORD-1001" -Headers @{"X-Correlation-ID"="corr-ca-03"} -ExpectedStatus @(200)

# CA-04: Idempotencia - Reintentar ORD-1001
$results += Test-Endpoint -Id "CA-04" -Name "Idempotencia reintento ORD-1001" -Method "POST" `
    -Url "$expUrl/orders" -Headers @{"X-Correlation-ID"="corr-ca-04"} -Body $bodyCa02 -ExpectedStatus @(409)

# CA-05: Validación cantidad <= 0
$bodyCa05 = @'
{
  "orderId": "ORD-1005-BADQTY",
  "customer": {
    "customerId": "CUST-002",
    "name": "Maria Lopez",
    "email": "maria.lopez@example.com"
  },
  "items": [
    {"sku": "LAP-001", "quantity": 0}
  ]
}
'@
$results += Test-Endpoint -Id "CA-05" -Name "Validación cantidad = 0" -Method "POST" `
    -Url "$expUrl/orders" -Headers @{"X-Correlation-ID"="corr-ca-05"} -Body $bodyCa05 -ExpectedStatus @(400)

# CA-06: Validación producto inexistente XXX-999
$bodyCa06 = @'
{
  "orderId": "ORD-1006-NOSKU",
  "customer": {
    "customerId": "CUST-003",
    "name": "Carlos Ruiz",
    "email": "carlos.ruiz@example.com"
  },
  "items": [
    {"sku": "XXX-999", "quantity": 1}
  ]
}
'@
$results += Test-Endpoint -Id "CA-06" -Name "Validación SKU inexistente XXX-999" -Method "POST" `
    -Url "$expUrl/orders" -Headers @{"X-Correlation-ID"="corr-ca-06"} -Body $bodyCa06 -ExpectedStatus @(404)

# CA-07: Validación stock insuficiente MON-001 (stock = 0)
$bodyCa07 = @'
{
  "orderId": "ORD-1007-NOSTOCK",
  "customer": {
    "customerId": "CUST-004",
    "name": "Ana Torres",
    "email": "ana.torres@example.com"
  },
  "items": [
    {"sku": "MON-001", "quantity": 1}
  ]
}
'@
$results += Test-Endpoint -Id "CA-07" -Name "Validación stock agotado MON-001" -Method "POST" `
    -Url "$expUrl/orders" -Headers @{"X-Correlation-ID"="corr-ca-07"} -Body $bodyCa07 -ExpectedStatus @(409)

# CA-08: Validación SKUs duplicados en pedido
$bodyCa08 = @'
{
  "orderId": "ORD-1008-DUPSKU",
  "customer": {
    "customerId": "CUST-005",
    "name": "David Gomez",
    "email": "david.gomez@example.com"
  },
  "items": [
    {"sku": "CAM-001", "quantity": 1},
    {"sku": "CAM-001", "quantity": 2}
  ]
}
'@
$results += Test-Endpoint -Id "CA-08" -Name "Validación SKUs duplicados" -Method "POST" `
    -Url "$expUrl/orders" -Headers @{"X-Correlation-ID"="corr-ca-08"} -Body $bodyCa08 -ExpectedStatus @(400)

# CA-09: Contingencia SF con orden ORD-1009
$bodyCa09 = @'
{
  "orderId": "ORD-1009-CONTINGENCY",
  "customer": {
    "customerId": "CUST-006",
    "name": "Laura Medina",
    "email": "laura.medina@example.com"
  },
  "items": [
    {"sku": "CAM-001", "quantity": 1}
  ]
}
'@
$results += Test-Endpoint -Id "CA-09" -Name "Contingencia/Alta ORD-1009" -Method "POST" `
    -Url "$expUrl/orders" -Headers @{"X-Correlation-ID"="corr-ca-09"} -Body $bodyCa09 -ExpectedStatus @(201, 202)

# CA-10: Reintento de sincronización manual
$results += Test-Endpoint -Id "CA-10" -Name "Reintento de Sync ORD-1009" -Method "POST" `
    -Url "$proUrl/orders/ORD-1009-CONTINGENCY/sync" -Headers @{"X-Correlation-ID"="corr-ca-10"} -ExpectedStatus @(200, 202)

# CA-11: Reporte CSV consolidado
$results += Test-Endpoint -Id "CA-11" -Name "Generación de Reporte CSV" -Method "GET" `
    -Url "$expUrl/orders/report" -Headers @{"Accept"="text/csv"; "X-Correlation-ID"="corr-ca-11"} -ExpectedStatus @(200)

Write-Host "`n=================================================================" -ForegroundColor Cyan
Write-Host "                       RESUMEN DE PRUEBAS                        " -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan
$results | Format-Table -AutoSize
