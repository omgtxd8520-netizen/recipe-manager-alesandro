# RecipeManager — Guía rápida de uso

Referencia rápida de la API. Para instalación completa, arquitectura y solución de
problemas, ver el [README](../README.md).

## Levantar el proyecto

```bash
docker compose up --build
docker compose exec web python scripts/seed.py   # datos de ejemplo (opcional)
```

- API: http://localhost:5000
- Swagger UI: http://localhost:5000/docs
- Jupyter Lab: http://localhost:8888

## Endpoints

| Método | Ruta                          | Descripción                                   |
|--------|-------------------------------|------------------------------------------------|
| GET    | `/`                            | Info de la API / frontend                     |
| GET    | `/recipes`                     | Lista recetas (`?q=`, `?ingredient=`, `?tag=`) |
| POST   | `/recipes`                     | Crea una receta                                |
| GET    | `/recipes/{id}`                | Obtiene una receta por id                      |
| PUT    | `/recipes/{id}`                | Reemplaza una receta                           |
| DELETE | `/recipes/{id}`                | Elimina una receta (y sus reseñas)             |
| GET    | `/users`                       | Lista usuarios                                 |
| POST   | `/users`                       | Crea un usuario (chef, foodie o admin)         |
| POST   | `/reviews`                     | Crea una reseña sobre una receta               |
| GET    | `/reviews/recipe/{recipe_id}`  | Lista las reseñas de una receta                |

## Ejemplos

```bash
# Buscar recetas con ajo
curl "http://localhost:5000/recipes?ingredient=ajo"

# Búsqueda de texto libre (título/tags)
curl "http://localhost:5000/recipes?q=pasta"

# Crear un usuario chef
curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"Ana","email":"ana@example.com","role":"chef"}' \
  http://localhost:5000/users

# Dejar una reseña
curl -X POST -H "Content-Type: application/json" \
  -d '{"recipe_id":"<id>","user_id":"<id>","rating":5,"comment":"Excelente"}' \
  http://localhost:5000/reviews
```
