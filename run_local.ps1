<#
run_local.ps1
Automatiza: crear venv, instalar dependencias, ejecutar tests y opcionalmente levantar Docker Compose y sembrar datos.
Uso:
  .\run_local.ps1           # crea venv, instala deps y ejecuta tests
  .\run_local.ps1 -StartDocker  # además levanta docker compose y siembra datos
#>
param(
    [switch] $StartDocker
)

Set-StrictMode -Version Latest

function Write-Ok($m){ Write-Host "[OK] $m" -ForegroundColor Green }
function Write-Err($m){ Write-Host "[ERR] $m" -ForegroundColor Red }

# Check Python
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { Write-Err "Python no está en PATH. Instala Python 3.11+ y reintenta."; exit 1 }

# Create venv
$venvPath = Join-Path $PSScriptRoot ".venv"
if (-not (Test-Path $venvPath)) {
    python -m venv $venvPath
    Write-Ok "Entorno virtual creado en $venvPath"
} else { Write-Ok "Entorno virtual existe: $venvPath" }

# Activate venv for this script
$activate = Join-Path $venvPath "Scripts\Activate.ps1"
if (Test-Path $activate) {
    . $activate
    Write-Ok "Entorno virtual activado"
} else {
    Write-Err "No se pudo activar entorno virtual: $activate"; exit 1
}

# Upgrade pip and install deps
python -m pip install --upgrade pip
pip install -r .\app\requirements.txt
Write-Ok "Dependencias instaladas"

# Run tests
Write-Host "Ejecutando tests..."
$tests = pytest -q
if ($LASTEXITCODE -ne 0) {
    Write-Err "Tests fallaron"
    exit $LASTEXITCODE
} else {
    Write-Ok "Tests pasaron"
}

if ($StartDocker) {
    # Start docker compose
    Write-Host "Levantando Docker Compose (en background)..."
    docker compose up --build -d
    if ($LASTEXITCODE -ne 0) { Write-Err "Fallo al levantar Docker Compose"; exit 1 }
    Write-Ok "Docker Compose levantado"

    # Wait briefly for Mongo
    Write-Host "Esperando algunos segundos para que Mongo inicie..."
    Start-Sleep -Seconds 6

    # Seed data
    Write-Host "Sembrando datos de ejemplo en el contenedor web..."
    docker compose exec web python scripts/seed.py
    if ($LASTEXITCODE -ne 0) { Write-Err "Fallo al sembrar datos" } else { Write-Ok "Datos sembrados" }

    Write-Host "Servicios disponibles: API http://localhost:5000, Jupyter http://localhost:8888 (ver token en logs)"
}

Write-Host "Listo. Para detener Docker: docker compose down"