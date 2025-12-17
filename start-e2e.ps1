# Natpudan AI - End-to-End Smoke Test Runner
# - Starts backend in background (port 8000)
# - Waits for health
# - Runs test-medical-ai.ps1
# - Stops backend and returns appropriate exit code

param(
    [int]$Port = 8000,
    [switch]$Verbose
)

$ErrorActionPreference = 'Continue'
$root    = Split-Path -Parent $MyInvocation.MyCommand.Path
$backend = Join-Path $root 'backend'

function Write-Status {
  param([string]$Message, [string]$Type = 'Info')
  $colors = @{ 'Success'='Green'; 'Error'='Red'; 'Warning'='Yellow'; 'Info'='Cyan' }
  Write-Host $Message -ForegroundColor $colors[$Type]
}

function Test-PortUsed {
  param([int]$Port)
  $c = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
  return ($null -ne $c)
}

function Remove-PortByNumber {
  param([int]$Port)
  $procs = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
  foreach($p in $procs){
    try { Stop-Process -Id $p.OwningProcess -Force -ErrorAction Stop; Write-Status "[PORT] Freed :$Port by killing PID $($p.OwningProcess)" 'Warning' } catch {}
  }
}

# Resolve Python in venv
$pyCandidates = @(
  (Join-Path $root '.venv\Scripts\python.exe'),
  (Join-Path $backend 'venv\Scripts\python.exe')
)
$python = $pyCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $python) {
  Write-Status '[ERROR] Could not locate Python in .venv. Please create venv and install deps.' 'Error'
  Write-Host 'Try:' -ForegroundColor Yellow
  Write-Host '  python -m venv .venv' -ForegroundColor Yellow
  Write-Host '  .\.venv\Scripts\Activate.ps1' -ForegroundColor Yellow
  Write-Host '  pip install -r backend\requirements.txt' -ForegroundColor Yellow
  exit 1
}

Write-Status "[SETUP] Root: $root" 'Info'
Write-Status "[SETUP] Backend: $backend" 'Info'
Write-Status "[SETUP] Python: $python" 'Info'
Write-Status "[STEP] Ensuring port :$Port is free" 'Info'
if (Test-PortUsed -Port $Port) { Remove-PortByNumber -Port $Port }

# Start backend in background job
Write-Status '[STEP] Starting backend...' 'Info'
$backendJob = Start-Job -ScriptBlock {
  param($dir, $py, $port)
  Set-Location $dir
  $env:PYTHONIOENCODING = 'utf-8'
  $env:PYTHONUTF8 = '1'
  & $py -m uvicorn app.main:app --host 127.0.0.1 --port $port 2>&1
} -ArgumentList $backend, $python, $Port

Start-Sleep -Milliseconds 800
Write-Status "[INFO] Backend job started (Id=$($backendJob.Id))" 'Info'

# Poll health
$healthy = $false
for($i=0;$i -lt 40;$i++){
  try {
    $r = Invoke-WebRequest -Uri "http://127.0.0.1:$Port/health" -UseBasicParsing -TimeoutSec 2
    if ($r.StatusCode -eq 200) { $healthy = $true; break }
  } catch {}
  Start-Sleep -Milliseconds 600
}

if (-not $healthy) {
  Write-Status '[ERROR] Backend did not become healthy in time' 'Error'
  Receive-Job -Id $backendJob.Id -Keep | Select-Object -Last 80
  Stop-Job -Id $backendJob.Id -ErrorAction SilentlyContinue
  exit 1
}
Write-Status '[OK] Backend healthy' 'Success'

# Run the test suite
$testScript = Join-Path $root 'test-medical-ai.ps1'
if (-not (Test-Path $testScript)) {
  Write-Status "[ERROR] Test script not found: $testScript" 'Error'
  Stop-Job -Id $backendJob.Id -ErrorAction SilentlyContinue
  exit 1
}

Write-Status '[STEP] Running end-to-end test...' 'Info'
& PowerShell -NoProfile -ExecutionPolicy Bypass -File $testScript
$testExit = $LASTEXITCODE

# Teardown backend
Write-Status '[STEP] Stopping backend...' 'Info'
Stop-Job -Id $backendJob.Id -ErrorAction SilentlyContinue
Receive-Job -Id $backendJob.Id -Keep | Select-Object -Last 20 | Out-Null

if ($Verbose) {
  Write-Host "\n[LOG] Backend tail:" -ForegroundColor Cyan
  Receive-Job -Id $backendJob.Id -Keep | Select-Object -Last 60
}

if ($testExit -eq 0) {
  Write-Status '[RESULT] E2E test passed ✅' 'Success'
  exit 0
} else {
  Write-Status "[RESULT] E2E test failed (exit=$testExit) ❌" 'Error'
  exit $testExit
}
