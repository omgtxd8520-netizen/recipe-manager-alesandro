# Universidad Nacional de Chilecito

## Equipo de Trabajo
* Alesandro David Fajardo Torres (davidfajardotorres777@gmail.com)

# RecipeManager
### Plataforma de Gestión y Descubrimiento de Recetas — Base de Datos · Universidad Nacional de Chilecito · 2026

![CI](https://github.com/omgtxd8520-netizen/recipe-manager-alesandro/actions/workflows/ci.yml/badge.svg)

---

## Descripción

RecipeManager es una API REST hecha en Flask sobre MongoDB para administrar recetas, autores y reseñas desde un mismo lugar, en vez de tenerlas repartidas entre notas del celular, capturas de pantalla y grupos de WhatsApp. Permite buscar recetas por texto, ingrediente o etiqueta, y calificarlas — así se distingue una receta realmente recomendada de una que solo suena bien.

El backend administra tres colecciones relacionadas entre sí (`recipes`, `users`, `reviews`) a través de una capa DAO (`RecipeManagerDAO`) que concentra toda la lógica de acceso a datos, para que el resto de la app no tenga que construir queries de MongoDB directamente.

Además del backend, el proyecto incluye:
- Documentación interactiva de la API vía Swagger/OpenAPI (`/docs`)
- Un frontend estático simple para navegar el catálogo de recetas
- Notebooks Jupyter para análisis exploratorio de las recetas cargadas
- Suite de tests unitarios e integración, con CI en GitHub Actions
- Datos de ejemplo (seed) para levantar una demo completa en minutos

---

## Arquitectura

```
Cliente (curl / Postman / frontend) → API REST (Flask + flask-restx)
                                              │
                                              ▼
                                     RecipeManagerDAO
                                              │
                                              ▼
                                    MongoDB (Docker)
                                  ┌─────────┼─────────┐
                              recipes     users     reviews
```

- **MongoDB**: 3 colecciones — `recipes` (recetas), `users` (autores/foodies), `reviews` (calificaciones y comentarios)
- **RecipeManagerDAO**: abstrae todas las operaciones sobre MongoDB en métodos con semántica de cocina (buscar por ingrediente, calcular rating promedio, listar reseñas de una receta)
- **Flask + flask-restx**: expone el DAO como API REST documentada automáticamente en `/docs`
- **RecipeAnalysis.ipynb**: notebook de demostración para explorar el dataset cargado

---

## Estructura del proyecto

```
recipe-manager-alesandro/
├── app/
│   ├── app.py                # API REST (Flask + flask-restx / Swagger)
│   ├── config.py              # Configuración interna de Flask
│   ├── dao.py                 # RecipeManagerDAO — interfaz principal con MongoDB
│   ├── db_models/
│   │   ├── recipe.py          # Documento de la colección recipes
│   │   ├── user.py            # Documento de la colección users
│   │   └── review.py          # Documento de la colección reviews
│   ├── static/index.html      # Frontend estático
│   └── requirements.txt       # Dependencias del backend
├── config_vars.py             # Variables de conexión (MONGO_URI, MONGO_DB_NAME)
├── setup_db.py                 # Inicialización de la BD e índices
├── scripts/seed.py             # Datos de prueba realistas (limpia y recarga)
├── data/sample_recipes.json    # Dataset de ejemplo para los notebooks
├── notebooks/RecipeAnalysis.ipynb  # Notebook de análisis exploratorio
├── tests/                       # Tests unitarios e integración
├── .postman/                    # Colección Postman lista para importar
├── docker-compose.yml           # MongoDB + API + Jupyter en contenedores
└── .github/workflows/ci.yml     # Integración continua
```

---

## Instalación

### Requisitos previos
- Git
- Docker Desktop (Windows/Mac/Linux) o Docker Engine + docker-compose
- Python 3.11+ (para desarrollo local sin Docker)
- curl (para probar endpoints desde terminal)

Verificá que estén instalados antes de continuar:
```bash
docker ps          # debe mostrar una tabla (aunque vacía)
git --version      # debe mostrar la versión instalada
```

### 1. Clonar el repositorio
```bash
git clone https://github.com/omgtxd8520-netizen/recipe-manager-alesandro.git
cd recipe-manager-alesandro
```

### 2. Configurar variables de entorno
```bash
cp .env.example .env
```
Este archivo no se sube al repositorio — está excluido por `.gitignore`.

### 3. Levantar los servicios con Docker Compose
```bash
docker compose up --build -d
```

Verificá que los contenedores estén corriendo:
```bash
docker ps
# deben aparecer los servicios web, mongo y jupyter con STATUS "Up"
```

### 4. Sembrar datos de ejemplo
```bash
docker compose exec web python scripts/seed.py
```

Resultado esperado:
```
[Semillero] Purgando base de datos...
[Semillero] Creando usuarios...
  Usuario creado: Gordon Ramsay (ID: ...)
  ...
[Semillero] Creando recetas...
  Receta creada: Beef Wellington (ID: ...)
  ...
[Semillero] Creando reseñas de los usuarios...
--OK-- Colección recipes — índices creados
--OK-- Colección reviews — índices creados
--OK-- Colección users — índices creados

[Semillero] Base de datos sembrada con éxito en esquema multi-colección relacional.
```

### 5. Servicios disponibles
- **API**: http://localhost:5000
- **Swagger UI (OpenAPI)**: http://localhost:5000/docs
- **Jupyter Lab**: http://localhost:8888 (el token aparece en `docker compose logs jupyter`)

---

## Desarrollo local (sin Docker, venv)

Windows (PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r app/requirements.txt
```

Linux / macOS
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r app/requirements.txt
```

Ejecutar la API localmente:
```bash
# Opción A — conectar al Mongo levantado con Docker Compose
export MONGO_URI='mongodb://localhost:27017/recipe_db'   # Linux/Mac
$env:MONGO_URI = 'mongodb://localhost:27017/recipe_db'    # PowerShell
python -m flask run --host=0.0.0.0

# Opción B — Mongo mock, solo para pruebas rápidas sin Docker
export MONGO_USE_MOCK=1
python -m flask run --host=0.0.0.0
```

---

## API — endpoints y ejemplos (curl / Postman)

```bash
# Listar todas las recetas
curl http://localhost:5000/recipes

# Búsqueda por ingrediente
curl "http://localhost:5000/recipes?ingredient=ajo"

# Crear una receta
curl -X POST -H "Content-Type: application/json" \
  -d '{"title":"Tostada","ingredients":["pan","aceite"],"tags":["desayuno"]}' \
  http://localhost:5000/recipes

# Obtener por id
curl http://localhost:5000/recipes/<id>

# Reemplazar (PUT)
curl -X PUT -H "Content-Type: application/json" \
  -d '{"title":"Nueva","ingredients":["x"]}' \
  http://localhost:5000/recipes/<id>

# Borrar
curl -X DELETE http://localhost:5000/recipes/<id>
```

Importá `.postman/RecipeManager.postman_collection.json` en Postman para tener la colección completa con ejemplos.

---

## Notebooks Jupyter

El servicio Jupyter se monta sobre `./notebooks` y `./data`, así que cualquier cambio en el notebook local se refleja en el contenedor.

1. `docker compose up --build`
2. Abrir http://localhost:8888 (token en `docker compose logs jupyter`)
3. Abrir `RecipeAnalysis.ipynb` y ejecutar para explorar recetas, ratings promedio y probar visualizaciones

---

## Pruebas y CI

El proyecto tiene un workflow de GitHub Actions en `.github/workflows/ci.yml` que instala dependencias, levanta un servicio Mongo en el runner, y ejecuta lint (flake8) y pytest en cada push.

Para reproducir la integración localmente:
```bash
docker compose up -d mongo
export MONGO_URI='mongodb://localhost:27017/recipe_db'   # Linux/Mac
$env:MONGO_URI = 'mongodb://localhost:27017/recipe_db'    # PowerShell
pytest -q
```

Linting:
```bash
flake8 --max-line-length=120 app
```

---

## Solución de problemas comunes

**Permisos Docker en Linux**
```bash
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker
```

**El seed falla o no encuentra archivos**
- Asegurate que `data/sample_recipes.json` existe y es legible.
- Si `docker compose exec web python scripts/seed.py` falla, corré el script desde el host apuntando al contenedor:
```bash
export MONGO_URI='mongodb://localhost:27017/recipe_db'
python scripts/seed.py
```

**Esperar a que Mongo esté listo en scripts/CI**
```bash
for i in {1..30}; do nc -z localhost 27017 && break || sleep 1; done
```

---

## Contribuir
1. Fork del repositorio
2. Crear rama `feature/<descripcion>`
3. Añadir tests para los cambios y ejecutar `pytest`
4. Abrir PR describiendo los cambios y los pasos para reproducirlos

## Licencia
MIT — ver archivo [LICENSE](LICENSE)
