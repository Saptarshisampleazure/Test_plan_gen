$ErrorActionPreference = 'Stop'

$root = Resolve-Path (Join-Path $PSScriptRoot '..')
$backend = Join-Path $root 'backend'
$python = Join-Path $backend '.venv\Scripts\python.exe'

function Test-BackendHealth {
  try {
    $response = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/health' -TimeoutSec 3 -UseBasicParsing
    return $response.StatusCode -eq 200
  }
  catch {
    return $false
  }
}

if (-not (Test-Path -LiteralPath $python)) {
  throw "Backend virtual environment was not found at $python"
}

Push-Location $root
try {
  npm.cmd run build
  if ($LASTEXITCODE -ne 0) {
    throw "Frontend build failed with exit code $LASTEXITCODE"
  }
}
finally {
  Pop-Location
}

Write-Host 'Starting Python backend with the built frontend mounted.'
Write-Host 'Open: http://127.0.0.1:8000/'

if (Test-BackendHealth) {
  Write-Host 'Python backend is already running at http://127.0.0.1:8000/'
  exit 0
}

Push-Location $backend
try {
  & $python -m uvicorn app.main:app --reload --reload-dir app --host 127.0.0.1 --port 8000
}
finally {
  Pop-Location
}
