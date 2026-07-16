import os
import time
import json
import sys

# Apuntar el app al servicio local Mongo en CI (o usar la del entorno de desarrollo)
os.environ.setdefault('MONGO_URI', 'mongodb://localhost:27017/recipe_db')

# Asegurar path para imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))

from app.app import app, recipes_col  # noqa: E402
from app.db_models.recipe import Recipe  # noqa: E402
from app.dao import RecipeDAO  # noqa: E402


recipe_dao = RecipeDAO(recipes_col)


def seed_if_empty():
    if recipes_col.count_documents({}) == 0:
        here = os.path.dirname(__file__)
        path = os.path.abspath(os.path.join(here, '..', 'data', 'sample_recipes.json'))
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if isinstance(data, list):
            for item in data:
                recipe = Recipe.from_dict(item)
                recipe_dao.create_recipe(recipe)


def test_integration_list_recipes():
    # Esperar un momento si Mongo se está levantando (CI runner)
    for _ in range(10):
        try:
            recipes_col.count_documents({})
            break
        except Exception:
            time.sleep(1)
    seed_if_empty()
    client = app.test_client()
    res = client.get('/recipes')
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1
