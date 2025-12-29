<#
.SYNOPSIS
Ultimate Podman TLS Fix - Extracts Proxy Certs from Host and Injects them into VM.
.DESCRIPTION
This script automatically detects the SSL certificate being used by your corporate proxy
to intercept Docker Hub traffic and injects it into the Podman machine's trust store.
#>

$ErrorActionPreference = "Stop"

Write-Host "--- Natpudan Ultimate TLS Fix ---" -ForegroundColor Cyan

# 1. Extract Proxy Cert from Host
Write-Host "[1/5] Extracting Proxy Certificate from Host connection..."
$targetUrl = "https://registry-1.docker.io"
try {
    # We use a web request to trigger the proxy/SSL handshake and capture the cert
    [Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}
    $webRequest = [System.Net.HttpWebRequest]::Create($targetUrl)
    $webRequest.Timeout = 5000
    try {
        $response = $webRequest.GetResponse()
        $cert = $webRequest.ServicePoint.Certificate
        $response.Close()
    } catch {
        # Even if it fails (401), we can usually get the cert from the ServicePoint
        $cert = $webRequest.ServicePoint.Certificate
    }

    if ($null -eq $cert) { throw "Could not capture certificate from $targetUrl" }

    $certBytes = $cert.Export([System.Security.Cryptography.X509Certificates.X509ContentType]::Cert)
    $tempCertPath = "$env:TEMP\proxy-captured.crt"
    [System.IO.File]::WriteAllBytes($tempCertPath, $certBytes)
    
    $subject = (New-Object System.Security.Cryptography.X509Certificates.X509Certificate2($tempCertPath)).Subject
    Write-Host "[OK] Captured Cert: $subject" -ForegroundColor Green
} catch {
    Write-Host "[!] Failed to capture cert from host: $_" -ForegroundColor Red
    exit 1
}

# 2. Ensure machine is running
$machine = "podman-machine-default"
Write-Host "[2/5] Checking Podman machine..."
$machines = podman machine list --format=json | ConvertFrom-Json
$m = $machines | Where-Object { $_.Name -eq $machine }
if (-not $m) { Write-Error "Machine not found."; exit 1 }
if ($m.Running -ne $true) { podman machine start; Start-Sleep -Seconds 5 }

# 3. Inject into Machine
Write-Host "[3/5] Injecting into Machine trust store..."
Get-Content $tempCertPath -Raw | podman machine ssh "cat > /tmp/proxy.crt"
podman machine ssh "sudo cp /tmp/proxy.crt /etc/pki/ca-trust/source/anchors/ && sudo update-ca-trust"

# 3. Configure Registries & Working Google Mirror
Write-Host "[3/5] Configuring Working Google Mirror (Bypasses Docker Hub 403 blocks)..."
$regConf = @"
unqualified-search-registries = ['mirror.gcr.io', 'docker.io']

[[registry]]
location = "docker.io"

[[registry.mirror]]
location = "mirror.gcr.io"

[[registry]]
location = 'quay.io'
insecure = true
"@

$regConf | podman machine ssh "sudo tee /etc/containers/registries.conf" | Out-Null

# 4. Clean up Proxy Garbage
Write-Host "[4/5] Cleaning up old proxy overrides..."
podman machine ssh "sudo rm -f /etc/systemd/system/podman.service.d/http-proxy.conf; sudo systemctl daemon-reload"

# 5. Restart & Test
Write-Host "[5/5] Restarting machine and testing the Mirror..."
podman machine stop
Start-Sleep -Seconds 2
podman machine start
Start-Sleep -Seconds 5

Write-Host "Testing pull with Google Mirror..." -ForegroundColor Yellow
podman pull redis:alpine

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n[SUCCESS] TLS FIX APPLIED! Podman is now using mirror.gcr.io to bypass blocks." -ForegroundColor Green
    Write-Host "You can now run: .\start-app.ps1" -ForegroundColor Cyan
} else {
    Write-Host "`n[!] Pull still failed. This usually means the Mirror is also blocked." -ForegroundColor Red
}
