$ErrorActionPreference = 'Stop'

$root = Resolve-Path (Join-Path $PSScriptRoot '..')
$backend = Join-Path $root 'backend'
$python = Join-Path $backend '.venv\Scripts\python.exe'

function Test-Port {
  param([int] $Port)

  $connection = Get-NetTCPConnection -LocalAddress '127.0.0.1' -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
  return $null -ne $connection
}

if (-not (Test-Path -LiteralPath $python)) {
  throw "Backend virtual environment was not found at $python"
}

if (-not (Test-Port 8000)) {
  Start-Process `
    -FilePath $python `
    -ArgumentList @('-m', 'uvicorn', 'app.main:app', '--reload', '--reload-dir', 'app', '--host', '127.0.0.1', '--port', '8000') `
    -WorkingDirectory $backend `
    -WindowStyle Hidden
}

if (-not (Test-Port 5173)) {
  Start-Process `
    -FilePath 'npm.cmd' `
    -ArgumentList @('run', 'dev:frontend') `
    -WorkingDirectory $root `
    -WindowStyle Hidden
}

Write-Host 'Backend:  http://127.0.0.1:8000/health'
Write-Host 'Frontend: http://127.0.0.1:5173/'
