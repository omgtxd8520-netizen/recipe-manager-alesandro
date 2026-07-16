RecipeManager - Usage

Running with Docker Compose:

- Start: `docker compose up --build`
- Seed data (optional): `docker compose exec web python scripts/seed.py`
- Access API: http://localhost:5000
- Access Jupyter Lab: http://localhost:8888

API endpoints

- GET / -> health
- GET /recipes -> list (supports ?q=, ?ingredient=, ?tag=)
- POST /recipes -> create
- GET /recipes/{id} -> retrieve
- PUT /recipes/{id} -> replace
- DELETE /recipes/{id} -> delete

Examples

curl "http://localhost:5000/recipes?ingredient=aceite"

