import os

# Cargar variables de entorno centralizadas (idéntico al esquema de SAVIA)
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://mongo:27017/recipe_db")
MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "recipe_db")
