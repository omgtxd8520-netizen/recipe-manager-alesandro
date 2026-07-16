# RecipeManager

Autor: Alesandro David Fajardo Torres

RecipeManager es una aplicación para almacenar, buscar y analizar recetas. Está pensada como proyecto educativo completo que incluye:

- API REST (Flask) usando MongoDB
- Docker Compose (MongoDB, API y Jupyter)
- Notebooks Jupyter para análisis y prototipado
- Tests y CI (GitHub Actions)
- Scripts de inicialización y ejemplo de Postman

Contenido principal

- app/: código de la API
- notebooks/: notebooks de análisis
- data/: datos de ejemplo (sample_recipes.json)
- scripts/: utilidades (sembrado de DB)

Ejecución local

1. Instalar Docker Desktop
2. Levantar servicios: `docker compose up --build`
3. Sembrar datos de ejemplo (opcional):
   - En otra terminal: `docker compose exec web python scripts/seed.py`
4. API: http://localhost:5000
5. Jupyter Lab: http://localhost:8888 (token en logs)

Ejemplos curl

- Listar recetas:
  curl http://localhost:5000/recipes

- Buscar por ingrediente:
  curl "http://localhost:5000/recipes?ingredient=ajo"

- Crear receta:
  curl -X POST -H "Content-Type: application/json" -d '{"title":"Tostada","ingredients":["pan","aceite"],"tags":["desayuno"]}' http://localhost:5000/recipes

CI

Hay una acción de GitHub Actions que ejecuta los tests con pytest.

Contribuir

1. Hacer fork y abrir PR
2. Añadir tests para cambios

Licencia: MIT
