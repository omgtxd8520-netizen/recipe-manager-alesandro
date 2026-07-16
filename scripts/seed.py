import os
import json
import sys
from pymongo import MongoClient

# Ajustar paths para importar desde el módulo del app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))

from app.db_models.recipe import Recipe  # noqa: E402
from app.dao import RecipeDAO  # noqa: E402

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://mongo:27017/recipe_db')
DB_NAME = os.environ.get('MONGO_DB_NAME', 'recipe_db')

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
recipes_col = db['recipes']

# Instanciar el DAO de recetas
recipe_dao = RecipeDAO(recipes_col)

here = os.path.dirname(__file__)
path = os.path.join(here, '..', 'data', 'sample_recipes.json')
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

if isinstance(data, list):
    # Limpiar colección física
    recipes_col.delete_many({})

    # Sembrar recetas utilizando la capa DAO y de Modelos
    count = 0
    for item in data:
        recipe = Recipe.from_dict(item)
        recipe_dao.create_recipe(recipe)
        count += 1

    # Re-crear índices idempotentes
    recipes_col.create_index([('title', 'text'), ('tags', 'text')])
    recipes_col.create_index('ingredients')
    print(f'Sembrado exitoso: se insertaron {count} recetas usando la capa DAO.')
else:
    print('No se encontraron recetas en el archivo de ejemplo.')
