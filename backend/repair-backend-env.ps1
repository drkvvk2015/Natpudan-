param(
    [switch]$Install,
    [switch]$RunTests,
    [switch]$RunIntegrationTests
)

$ErrorActionPreference = "Stop"
$backendDir = if ($PSScriptRoot) { $PSScriptRoot } else { (Get-Location).Path }
Set-Location $backendDir

function Write-Status {
    param([string]$Message, [string]$Type = "Info")
    $colors = @{ "Info"="Cyan"; "Success"="Green"; "Warning"="Yellow"; "Error"="Red" }
    Write-Host $Message -ForegroundColor $colors[$Type]
}

function Resolve-PythonInterpreter {
    $venvCandidates = @(
        (Join-Path $backendDir "..\.venv311\Scripts\python.exe"),
        (Join-Path $backendDir "..\.venv\Scripts\python.exe"),
        (Join-Path $backendDir ".venv\Scripts\python.exe")
    )

    foreach ($candidate in $venvCandidates) {
        if (Test-Path $candidate) {
            try {
                & $candidate --version | Out-Null
                if ($LASTEXITCODE -eq 0) {
                    return (Resolve-Path $candidate).Path
                }
            } catch {}
        }
    }

    try {
        $py311 = & py -3.11 -c "import sys; print(sys.executable)" 2>$null
        if ($LASTEXITCODE -eq 0 -and $py311) {
            return $py311.Trim()
        }
    } catch {}

    return $null
}

Write-Status "Checking backend runtime..." "Info"
$python = Resolve-PythonInterpreter
if (-not $python) {
    Write-Status "Python 3.11 was not found. Install Python 3.11 and recreate .venv311." "Error"
    exit 1
}
Write-Status "Using Python: $python" "Success"

$version = & $python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"
Write-Status "Python version: $version" "Info"

if ($version -notlike "3.11.*") {
    Write-Status "Recommended Python is 3.11.x for best package compatibility. Current: $version" "Warning"
}

if ($Install) {
    Write-Status "Installing backend dependencies..." "Info"
    & $python -m pip install --upgrade pip
    & $python -m pip install -r requirements.txt
    & $python -m pip install -r requirements-db.txt
    Write-Status "Dependency installation complete" "Success"
}

Write-Status "Validating critical imports..." "Info"
& $python -c "import fastapi,uvicorn,sqlalchemy; from app.main import app; print('Backend imports OK')"
Write-Status "Import validation succeeded" "Success"

if ($RunTests) {
    if (-not $Install) {
        Write-Status "Ensuring test dependencies are installed..." "Info"
        & $python -m pip install -r requirements-test.txt
    } else {
        & $python -m pip install -r requirements-test.txt
    }
    Write-Status "Running backend test smoke suite..." "Info"
    & $python -m pytest tests -q
}

if ($RunIntegrationTests) {
    Write-Status "Running integration tests (requires local API on :8001)..." "Info"

    $serverJob = Start-Job -ScriptBlock {
        param($workingDir, $pythonPath)
        Set-Location $workingDir
        & $pythonPath -m uvicorn app.main:app --host 127.0.0.1 --port 8001
    } -ArgumentList $backendDir, $python

    try {
        $healthy = $false
        for ($i = 0; $i -lt 20; $i++) {
            try {
                $resp = Invoke-WebRequest -Uri "http://127.0.0.1:8001/health" -UseBasicParsing -TimeoutSec 2
                if ($resp.StatusCode -eq 200) {
                    $healthy = $true
                    break
                }
            } catch {}
            Start-Sleep -Milliseconds 500
        }

        if (-not $healthy) {
            Write-Status "Integration server did not become healthy on time" "Error"
            exit 1
        }

        & $python -m pytest tests/test_auth.py -q
    }
    finally {
        if ($serverJob) {
            Stop-Job -Job $serverJob -Force -ErrorAction SilentlyContinue
            Remove-Job -Job $serverJob -Force -ErrorAction SilentlyContinue
        }
    }
}

Write-Status "Backend runtime check complete" "Success"
