# RecipeManager

Autor: Alesandro David Fajardo Torres

RecipeManager es un proyecto educativo y demostrativo para gestionar recetas: almacenar, buscar, analizar y prototipar ideas con Jupyter.

Badges

![CI](https://github.com/omgtxd8520-netizen/recipe-manager-alesandro/actions/workflows/ci.yml/badge.svg)

Índice

- [Descripción](#descripción)
- [Características](#características)
- [Tecnologías](#tecnologías)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Rápido inicio (Docker)](#rápido-inicio-docker)
- [Desarrollo local (venv)](#desarrollo-local-venv)
- [API – Resumen de endpoints](#api--resumen-de-endpoints)
- [Notebooks y análisis](#notebooks-y-análisis)
- [Tests y CI](#tests-y-ci)
- [Contribuir](#contribuir)
- [Licencia](#licencia)

Descripción

Proyecto de ejemplo completo que demuestra una pequeña pila web: Flask REST API, MongoDB (contenedor Docker), Jupyter notebooks para análisis y pruebas, scripts de inicialización, pruebas unitarias e integración, y despliegue local con Docker Compose.

Características

- CRUD de recetas (título, ingredientes, tags, porciones)
- Búsqueda por texto, ingrediente y tag
- Documentación automática Swagger (/docs)
- Notebook Jupyter con ejemplos de análisis de datos
- Script para poblar la base de datos con datos de ejemplo
- GitHub Actions CI con tests e integración contra Mongo
- Pequeña interfaz estática para pruebas rápidas

Tecnologías

- Python 3.11
- Flask + flask-restx (OpenAPI/Swagger)
- MongoDB (contenedor Docker)
- Jupyter Lab (imagen oficial)
- Docker Compose
- pytest, mongomock para pruebas

Estructura del repositorio

- app/ — código fuente de la API y recursos estáticos
- data/ — datos de ejemplo (sample_recipes.json)
- notebooks/ — Jupyter notebooks para análisis
- scripts/ — utilidades (p. ej. seed.py)
- tests/ — pruebas unitarias e integración
- .github/workflows/ — CI

Rápido inicio (Docker)

Requisitos: Docker Desktop (Windows/Mac/Linux)

1. Clonar el repositorio
2. En la raíz del proyecto ejecutar:

   docker compose up --build

3. (Opcional) Sembrar datos de ejemplo desde el contenedor web:

   docker compose exec web python scripts/seed.py

4. Servicios:
- API: http://localhost:5000
- Swagger UI: http://localhost:5000/docs
- Jupyter Lab: http://localhost:8888 (token en logs)

Desarrollo local (Virtualenv)

1. Crear y activar un entorno virtual (Windows PowerShell):

   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

2. Instalar dependencias:

   pip install -r app/requirements.txt

3. Ejecutar tests:

   pytest -q

4. Ejecutar localmente (usa la misma variable MONGO_URI si quieres conectar al contenedor):

   set MONGO_URI=mongodb://localhost:27017/recipe_db  # Windows (PowerShell: $env:MONGO_URI = '...')
   python -m flask run --host=0.0.0.0

API – Resumen de endpoints

- GET /recipes — lista recetas (query params: q, ingredient, tag)
- POST /recipes — crea receta (JSON body)
- GET /recipes/{id} — obtiene receta
- PUT /recipes/{id} — reemplaza receta
- DELETE /recipes/{id} — elimina receta
- GET /docs — documentación Swagger (OpenAPI)

Ejemplos curl

Listar recetas:

  curl http://localhost:5000/recipes

Buscar por ingrediente:

  curl "http://localhost:5000/recipes?ingredient=ajo"

Crear receta:

  curl -X POST -H "Content-Type: application/json" -d '{"title":"Tostada","ingredients":["pan","aceite"],"tags":["desayuno"]}' http://localhost:5000/recipes

Notebooks y análisis

Abrir Jupyter Lab en http://localhost:8888 y ejecutar `notebooks/RecipeAnalysis.ipynb`. El notebook carga `data/sample_recipes.json` y muestra ejemplos de agregaciones y visualizaciones con pandas.

Tests y CI

- Tests: pytest (tests unitarios e integración). En CI se levanta un servicio Mongo y se ejecutan los tests.
- Ejecutar localmente: `pytest -q`

Contribuir

1. Hacer fork y crear una rama descriptiva: `feature/<algo>`
2. Agregar tests para nuevas funcionalidades
3. Abrir PR explicando el cambio

Siéntete libre de abrir issues o PRs con mejoras. Sigue las guías de estilo y agrega tests.

Contacto

Autor: Alesandro David Fajardo Torres — usa el repositorio para practicar, clonar y adaptar a tus proyectos.

Licencia

Este proyecto está bajo la Licencia MIT — ver archivo LICENSE para detalles.

