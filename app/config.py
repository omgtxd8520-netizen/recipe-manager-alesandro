import os

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://mongo:27017/recipe_db')
