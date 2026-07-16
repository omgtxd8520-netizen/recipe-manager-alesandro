from pymongo import MongoClient
from config_vars import MONGO_URI, MONGO_DB_NAME


def setup():
    """
    Inicializa la base de datos de RecipeManager.
    Crea las colecciones necesarias y sus índices correspondientes.
    Es seguro ejecutarlo múltiples veces (idempotente) sin borrar datos.
    """
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB_NAME]

    # Colección: recipes
    recipes = db["recipes"]
    recipes.create_index([('title', 'text'), ('tags', 'text')])
    recipes.create_index('ingredients')
    recipes.create_index('author_id')
    print("--OK-- Colección recipes — índices creados")

    # Colección: reviews
    reviews = db["reviews"]
    reviews.create_index('recipe_id')
    reviews.create_index('user_id')
    print("--OK-- Colección reviews — índices creados")

    # Colección: users
    users = db["users"]
    users.create_index('username', unique=True)
    users.create_index('email', unique=True)
    print("--OK-- Colección users — índices creados")

    client.close()
    print(f"\n--OK-- Base de datos '{MONGO_DB_NAME}' inicializada con éxito.")


if __name__ == "__main__":
    setup()
