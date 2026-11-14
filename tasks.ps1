# AgroTwin developer tasks for Windows PowerShell (GNU make is not required).
# AI-generated under human review (opencode/big-pickle, 2026-11-14). See docs/AI_USE.md.
param(
    [Parameter(Position = 0)]
    [ValidateSet('help', 'install', 'test', 'validate', 'lint', 'api', 'web', 'demo', 'version', 'clean')]
    [string]$Task = 'help'
)

$ErrorActionPreference = 'Stop'
$Python = if ($env:PYTHON) { $env:PYTHON } else { 'python' }

function Invoke-Checked {
    param([scriptblock]$Block)
    & $Block
    if (-not $?) { exit 1 }
}

switch ($Task) {
    'help' {
        $v = & $Python -c "import agrotwin; print(agrotwin.__version__)"
        Write-Host "AgroTwin $v"
        Write-Host "  .\tasks.ps1 install   install runtime + dev dependencies"
        Write-Host "  .\tasks.ps1 test      run unit, contract and smoke tests"
        Write-Host "  .\tasks.ps1 validate  validate contract fixtures"
        Write-Host "  .\tasks.ps1 lint      run ruff"
        Write-Host "  .\tasks.ps1 api       run FastAPI on http://127.0.0.1:8000"
        Write-Host "  .\tasks.ps1 web       run Next.js (npm install in web/ first)"
        Write-Host "  .\tasks.ps1 demo      run the API in fixture-backed demo mode"
        Write-Host "  .\tasks.ps1 version   print the single-source version"
        Write-Host "  .\tasks.ps1 clean     remove local caches"
    }
    'install' {
        Invoke-Checked { & $Python -m pip install -r requirements-dev.txt }
        Invoke-Checked { & $Python -m pip install -r requirements-api.txt }
    }
    'test' { Invoke-Checked { & $Python -m pytest } }
    'validate' { Invoke-Checked { & $Python -m contracts.validate --all } }
    'lint' { Invoke-Checked { & $Python -m ruff check . } }
    'api' { Invoke-Checked { & $Python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload } }
    'web' { Invoke-Checked { npm --prefix web run dev } }
    'demo' { Invoke-Checked { & $Python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 } }
    'version' { & $Python -c "import agrotwin; print(agrotwin.__version__)" }
    'clean' {
        Get-ChildItem -Path . -Recurse -Directory -Filter '__pycache__' -ErrorAction SilentlyContinue |
            Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
        foreach ($p in @('.pytest_cache', '.ruff_cache')) {
            if (Test-Path -LiteralPath $p) { Remove-Item -LiteralPath $p -Recurse -Force }
        }
    }
}
