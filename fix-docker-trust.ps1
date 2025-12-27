<#
fix-docker-trust.ps1
Purpose:
- Ensure Docker CLI is available in this session (PATH fallback)
- Install corporate Root CA into Docker Desktop daemon trust and per-host trust
- Restart Docker Desktop and wait until the daemon is ready
- Sanity-test image pulls (redis/nginx/postgres)
- Optionally run your deploy script

Usage examples:
  # If you already exported the corporate root CA to Downloads:
  .\fix-docker-trust.ps1 -CertPath "$env:USERPROFILE\Downloads\corporate-root-ca.crt" -TestPulls -RunDeploy

  # If you know the thumbprint of the corporate root CA in Windows store:
  .\fix-docker-trust.ps1 -Thumbprint "PUT_ACTUAL_THUMBPRINT_HERE" -TestPulls

  # If you don’t know the CA yet, run without params and choose from the candidate list:
  .\fix-docker-trust.ps1 -Interactive -TestPulls

Notes:
- The CA must be the corporate SSL inspection root (Zscaler/Fortinet/etc.), NOT a Microsoft/public root.
- After installing the CA, Docker Desktop must be restarted for trust to apply.
#>

param(
  [string]$CertPath,
  [string]$Thumbprint,
  [switch]$Interactive,
  [switch]$SetUserPath,   # permanently add docker cli to USER PATH (no admin required)
  [switch]$TestPulls,
  [switch]$RunDeploy
)

$ErrorActionPreference = "Stop"

function Ensure-SessionDockerPath {
  # Add common Docker CLI paths for THIS session (no admin required)
  $paths = @(
    "C:\Program Files\Docker\Docker\resources\bin",
    "C:\Program Files\Docker\cli-plugins"
  )
  foreach ($p in $paths) {
    if (Test-Path $p) { $env:Path += ";$p" }
  }
}

function Set-UserDockerPath {
  # Permanently add docker cli to USER PATH (no admin required)
  $paths = @(
    "C:\Program Files\Docker\Docker\resources\bin",
    "C:\Program Files\Docker\cli-plugins"
  )
  $userPath = [Environment]::GetEnvironmentVariable("Path","User")
  foreach ($p in $paths) {
    if ((Test-Path $p) -and ($userPath -notlike "*$p*")) { $userPath += ";$p" }
  }
  [Environment]::SetEnvironmentVariable("Path", $userPath, "User")
  Write-Host "[OK] USER PATH updated. You must restart PowerShell for permanent PATH changes to take effect." -ForegroundColor Yellow
}

function Get-DockerCmd {
  $cmd = (Get-Command docker -ErrorAction SilentlyContinue).Path
  if ($cmd) { return $cmd }
  $candidates = @(
    "C:\Program Files\Docker\Docker\resources\bin\docker.exe",
    "C:\Program Files\Docker\Docker\resources\bin\com.docker.cli.exe"
  )
  foreach ($c in $candidates) { if (Test-Path $c) { return $c } }
  throw "Docker CLI not found. Ensure Docker Desktop is installed, started, and CLI is available."
}

function Wait-DockerReady {
  param([int]$MaxSeconds=120)
  $DockerCmd = Get-DockerCmd
  $start = Get-Date
  while ((New-TimeSpan -Start $start -End (Get-Date)).TotalSeconds -lt $MaxSeconds) {
    try {
      & $DockerCmd info | Out-Null
      Write-Host "[OK] Docker daemon is ready." -ForegroundColor Green
      return
    } catch {
      Start-Sleep -Seconds 3
    }
  }
  throw "Docker daemon did not become ready within $MaxSeconds seconds."
}

function Restart-DockerDesktop {
  # Gracefully restart Docker Desktop app
  Write-Host "[Restart] Restarting Docker Desktop..." -ForegroundColor Cyan
  Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
  $desktopExe = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
  if (-not (Test-Path $desktopExe)) {
    Write-Warning "Docker Desktop executable not found at $desktopExe. Please start Docker Desktop manually."
  } else {
    Start-Process -FilePath $desktopExe | Out-Null
  }
  Start-Sleep -Seconds 5
  Wait-DockerReady -MaxSeconds 180
}

function Get-CandidateCorporateRoots {
  # List likely corporate root CAs (exclude common public/Microsoft roots)
  Get-ChildItem Cert:\LocalMachine\Root, Cert:\CurrentUser\Root |
    Where-Object {
      $_.Subject -notmatch 'Microsoft|DigiCert|GlobalSign|ISRG|Amazon|Google|Entrust|Sectigo|USERTRUST|Let''s Encrypt|QuoVadis|IdenTrust|COMODO'
    } |
    Select-Object Subject, Issuer, Thumbprint |
    Sort-Object Subject
}

function Export-RootCA {
  param([string]$Thumbprint, [string]$Destination)
  $certPathLM = "Cert:\LocalMachine\Root\$Thumbprint"
  $certPathCU = "Cert:\CurrentUser\Root\$Thumbprint"
  if (Test-Path $certPathLM) {
    Export-Certificate -Cert $certPathLM -FilePath $Destination | Out-Null
  } elseif (Test-Path $certPathCU) {
    Export-Certificate -Cert $certPathCU -FilePath $Destination | Out-Null
  } else {
    throw "Certificate with Thumbprint $Thumbprint not found in Root stores."
  }
  if (-not (Test-Path $Destination)) { throw "Export failed: $Destination not created." }
}

function Install-CorporateCA {
  param([string]$PathToCA)

  if (-not (Test-Path $PathToCA)) { throw "CA file not found at $PathToCA" }

  # Global daemon trust (Desktop imports these certs on restart)
  $globalDaemonTrust = Join-Path $env:APPDATA "Docker\certs.d"
  New-Item -ItemType Directory -Path $globalDaemonTrust -Force | Out-Null
  Copy-Item $PathToCA (Join-Path $globalDaemonTrust 'corporate-root-ca.crt') -Force
  Write-Host "[OK] Installed corporate CA into $globalDaemonTrust" -ForegroundColor Green

  # Per-host trust (helps CDN endpoints)
  $perHostTargets = @(
    "$env:USERPROFILE\.docker\certs.d\registry-1.docker.io",
    "$env:USERPROFILE\.docker\certs.d\production.cloudflare.docker.com",
    "$env:USERPROFILE\.docker\certs.d\docker-images-prod.6aa30f8b08e16409b46e0173d6de2f56.r2.cloudflarestorage.com"
  )
  foreach ($p in $perHostTargets) {
    New-Item -ItemType Directory -Path $p -Force | Out-Null
    Copy-Item $PathToCA (Join-Path $p 'ca.crt') -Force
  }
  Write-Host "[OK] Installed per-host CA trust entries." -ForegroundColor Green
}

function Test-Pulls {
  $DockerCmd = Get-DockerCmd
  $images = @("redis:7-alpine", "nginx:alpine", "postgres:15-alpine")
  foreach ($img in $images) {
    Write-Host "[Pull] $img" -ForegroundColor Cyan
    & $DockerCmd pull $img
  }
}

function Run-DeployScript {
  if (Test-Path ".\deploy-production.ps1") {
    Write-Host "[Deploy] Running deploy-production.ps1 -Recreate" -ForegroundColor Cyan
    .\deploy-production.ps1 -Recreate
  } else {
    Write-Warning "deploy-production.ps1 not found in current directory."
  }
}

# --- Main flow ---

# 0) Optional: permanently add docker cli to USER PATH
if ($SetUserPath) { Set-UserDockerPath }

# Ensure docker CLI available for THIS session
Ensure-SessionDockerPath
# Verify docker works
try {
  & (Get-DockerCmd) --version | Write-Host
  & (Get-DockerCmd) compose version | Write-Host
} catch {
  Write-Warning "Docker CLI not immediately available. Continuing; script will call Docker by full path."
}

# 1) Acquire corporate Root CA
$destination = "$env:USERPROFILE\Downloads\corporate-root-ca.crt"

if ($CertPath) {
  if (-not (Test-Path $CertPath)) { throw "Specified -CertPath does not exist: $CertPath" }
  if ($CertPath -ne $destination) { Copy-Item $CertPath $destination -Force }
} elseif ($Thumbprint) {
  Export-RootCA -Thumbprint $Thumbprint -Destination $destination
} elseif ($Interactive) {
  Write-Host "Listing candidate corporate root CAs (exclude common public/Microsoft roots)..." -ForegroundColor Yellow
  $candidates = Get-CandidateCorporateRoots
  if (-not $candidates -or $candidates.Count -eq 0) {
    Write-Warning "No non-public root CAs found. Use browser to export the inspection root CA as Base-64 .cer and pass -CertPath."
    throw "Corporate CA not identified."
  }
  $i = 0
  $candidates | ForEach-Object { $i++; Write-Host ("[{0}] Subject={1} | Issuer={2} | Thumbprint={3}" -f $i, $_.Subject, $_.Issuer, $_.Thumbprint) }
  $choice = Read-Host "Enter the number of the corporate root CA to export"
  $selected = $candidates[[int]$choice - 1]
  Export-RootCA -Thumbprint $selected.Thumbprint -Destination $destination
} else {
  Write-Warning "No -CertPath or -Thumbprint provided. The simplest way: export your corporate root CA from the browser (padlock → certificate → top-of-chain) to $destination, then re-run with -CertPath."
  throw "Corporate CA is required to fix TLS trust for Docker pulls."
}

Write-Host "[OK] Corporate CA prepared at $destination" -ForegroundColor Green

# 2) Install CA into Docker trust (daemon + per-host)
Install-CorporateCA -PathToCA $destination

# 3) Restart Docker Desktop and wait until daemon ready
Restart-DockerDesktop

# 4) Optional: Test pulls
if ($TestPulls) { Test-Pulls }

# 5) Optional: Run deploy
if ($RunDeploy) { Run-DeployScript }

Write-Host "[DONE] Trust fix complete." -ForegroundColor Green
