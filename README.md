# RecipeManager

**Autor:** Alesandro David Fajardo Torres

Badges

![CI](https://github.com/omgtxd8520-netizen/recipe-manager-alesandro/actions/workflows/ci.yml/badge.svg)

Índice

- [Descripción](#descripción)
- [Requisitos](#requisitos)
- [Instalación y uso rápido (Docker)](#instalación-y-uso-rápido-docker)
- [Desarrollo local (venv)](#desarrollo-local-venv)
- [Comandos útiles de Docker y debugging](#comandos-útiles-de-docker-y-debugging)
- [API — endpoints y ejemplos (curl/Postman)](#api--endpoints-y-ejemplos-curlpostman)
- [Notebooks Jupyter](#notebooks-jupyter)
- [Pruebas y CI](#pruebas-y-ci)
- [Linting y calidad de código](#linting-y-calidad-de-código)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Solución de problemas comunes](#solución-de-problemas-comunes)
- [Contribuir](#contribuir)
- [Licencia](#licencia)

Descripción

RecipeManager es una aplicación educativa que demuestra una pila completa: API REST en Flask, persistencia con MongoDB (contenedor Docker), Jupyter notebooks para análisis y prototipos, tests (unitarios e integración), CI con GitHub Actions y utilidades para desarrollo y despliegue.

Requisitos

- Git
- Docker Desktop (Windows/Mac/Linux) o Docker Engine + docker-compose
- Python 3.11+ (para desarrollo local)
- curl (para probar endpoints desde terminal)

Instalación y uso rápido (Docker)

1) Clonar el repositorio

  git clone https://github.com/omgtxd8520-netizen/recipe-manager-alesandro.git
  cd recipe-manager-alesandro

2) Copiar variables de entorno (si aplica)

  cp .env.example .env  # crearás variables si las necesitas (opcional)

3) Levantar servicios con Docker Compose

  docker compose up --build

  # O en background
  docker compose up --build -d

4) Sembrar datos de ejemplo (desde host):

  docker compose exec web python scripts/seed.py

5) Servicios disponibles

- API: http://localhost:5000
- Swagger UI (OpenAPI): http://localhost:5000/docs
- Jupyter Lab: http://localhost:8888  (token aparece en los logs del contenedor jupyter)

Desarrollo local (venv)

Windows (PowerShell)

  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  python -m pip install --upgrade pip
  pip install -r app/requirements.txt

Linux / macOS

  python3 -m venv .venv
  source .venv/bin/activate
  python -m pip install --upgrade pip
  pip install -r app/requirements.txt

Ejecutar la API localmente (conecta a Mongo local o contenedor)

# Opción A — conectar al Mongo que levantaste con Docker Compose
$env:MONGO_URI = 'mongodb://localhost:27017/recipe_db'  # PowerShell
python -m flask run --host=0.0.0.0

# Opción B — usar Mongo mock (solo para tests rápidos)
$env:MONGO_USE_MOCK = '1'
python -m flask run --host=0.0.0.0

Pruebas (pytest)

# Ejecutar tests unitarios
pytest -q tests/test_app.py

# Ejecutar todos los tests (unit + integración)
# Asegúrate de que un servicio Mongo esté disponible (docker compose up -d)
pytest -q

Comandos útiles de Docker y debugging

# Ver contenedores en ejecución
docker ps

# Ver logs (seguimiento)
docker compose logs -f web

# Acceder al shell del contenedor web
docker compose exec web sh

# Acceder a la shell de MongoDB (si el contenedor se llama "recipe_mongo")
docker exec -it recipe_mongo mongo

# Parar servicios
docker compose down

# Reconstruir imágenes
docker compose build --no-cache

API — endpoints y ejemplos (curl/Postman)

# Listar todas las recetas
curl http://localhost:5000/recipes

# Búsqueda por ingrediente
curl "http://localhost:5000/recipes?ingredient=ajo"

# Crear una receta
curl -X POST -H "Content-Type: application/json" -d '{"title":"Tostada","ingredients":["pan","aceite"],"tags":["desayuno"]}' http://localhost:5000/recipes

# Obtener por id
curl http://localhost:5000/recipes/<id>

# Reemplazar (PUT)
curl -X PUT -H "Content-Type: application/json" -d '{"title":"Nueva","ingredients":["x"]}' http://localhost:5000/recipes/<id>

# Borrar
curl -X DELETE http://localhost:5000/recipes/<id>

Postman

Importa `.postman/RecipeManager.postman_collection.json` en Postman para tener las colecciones y ejemplos listos.

Notebooks Jupyter

El servicio Jupyter se monta sobre ./notebooks y ./data, por lo tanto cualquier cambio en el notebook local se refleja en el contenedor.

Abrir Jupyter Lab (después de docker compose up):

- URL: http://localhost:8888
- Token: aparece en logs del contenedor jupyter (docker compose logs jupyter)

Pruebas e integración en CI

El proyecto tiene un workflow GitHub Actions en `.github/workflows/ci.yml` que:

- instala dependencias
- arranca un servicio Mongo en el runner
- espera a que Mongo esté listo
- ejecuta lint (flake8) y pytest

Si necesitas reproducir la integración localmente:

1. Levantar el servicio Mongo con docker compose:

  docker compose up -d mongo

2. Exportar la variable de entorno usada por los tests:

  export MONGO_URI='mongodb://localhost:27017/recipe_db'  # Linux/Mac
  $env:MONGO_URI = 'mongodb://localhost:27017/recipe_db' # PowerShell

3. Ejecutar pytest

  pytest -q

Linting y calidad de código

Se incluye flake8 en `app/requirements.txt`. Para ejecutar localmente:

  flake8 --max-line-length=120 app

Estructura del repositorio

- app/ — código de la API (Flask + OpenAPI) y static
- data/ — `sample_recipes.json`
- notebooks/ — Jupyter notebooks (RecipeAnalysis.ipynb)
- scripts/ — utilidades (seed.py)
- tests/ — pruebas unitarias e integración
- .github/workflows/ci.yml — integración continua

Solución de problemas comunes

Permisos Docker en Linux

Si obtienes errores de permiso al ejecutar comandos Docker en Linux:

  sudo groupadd docker
  sudo usermod -aG docker $USER
  newgrp docker

Problemas con el seed o acceso a archivos

- Asegúrate que `data/sample_recipes.json` existe y sea legible.
- Si `docker compose exec web python scripts/seed.py` falla, prueba ejecutar el script desde el host con el MONGO_URI apuntando al contenedor:

  export MONGO_URI='mongodb://localhost:27017/recipe_db'
  python scripts/seed.py

Trucos para esperar a Mongo en scripts

En CI y scripts de inicialización puede ser necesario esperar a que Mongo acepte conexiones; ejemplo simple en bash:

  for i in {1..30}; do nc -z localhost 27017 && break || sleep 1; done

Contribuir

1. Fork del repositorio
2. Crear rama `feature/<descripcion>`
3. Añadir tests para cambios y ejecutar `pytest`
4. Abrir PR describiendo los cambios y pasos para reproducir

Licencia

MIT — ver archivo LICENSE

