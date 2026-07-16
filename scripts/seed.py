import os
import json
from pymongo import MongoClient

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://mongo:27017/recipe_db')
DB_NAME = os.environ.get('MONGO_DB_NAME', 'recipe_db')

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
recipes = db['recipes']

here = os.path.dirname(__file__)
path = os.path.join(here, '..', 'data', 'sample_recipes.json')
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

if isinstance(data, list):
    # clear collection and insert
    recipes.delete_many({})
    recipes.insert_many(data)
    recipes.create_index([('title', 'text'), ('tags', 'text')])
    recipes.create_index('ingredients')
    print('Inserted', len(data), 'recipes')
else:
    print('No recipes found in sample file')
