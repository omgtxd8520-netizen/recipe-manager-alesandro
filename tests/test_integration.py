import os
import time
import json

# Point app to local Mongo service in CI (or developer can set MONGO_URI locally)
os.environ.setdefault('MONGO_URI', 'mongodb://localhost:27017/recipe_db')

from app.app import app, recipes_col


def seed_if_empty():
    if recipes_col.count_documents({}) == 0:
        here = os.path.dirname(__file__)
        path = os.path.abspath(os.path.join(here, '..', 'data', 'sample_recipes.json'))
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if isinstance(data, list):
            recipes_col.insert_many(data)


def test_integration_list_recipes():
    # wait a bit if Mongo is still coming up (CI runner)
    for _ in range(10):
        try:
            # simple ping by counting
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
