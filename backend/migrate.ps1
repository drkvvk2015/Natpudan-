param(
    [ValidateSet('current', 'history', 'upgrade', 'revision')]
    [string]$Command = 'current',
    [string]$Message = 'schema update'
)

$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

$python = if (Test-Path "..\.venv\Scripts\python.exe") {
    Resolve-Path "..\.venv\Scripts\python.exe"
} elseif (Test-Path "..\.venv311\Scripts\python.exe") {
    Resolve-Path "..\.venv311\Scripts\python.exe"
} else {
    'python'
}

switch ($Command) {
    'current' { & $python -m alembic current }
    'history' { & $python -m alembic history }
    'upgrade' { & $python -m alembic upgrade head }
    'revision' { & $python -m alembic revision --autogenerate -m $Message }
}
