import os
import time
import sys

# Apuntar el app al servicio local Mongo en CI (o usar la del entorno de desarrollo)
os.environ.setdefault('MONGO_URI', 'mongodb://localhost:27017/recipe_db')

# Asegurar path para imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))

from app.app import app, db  # noqa: E402
from app.db_models.recipe import Recipe  # noqa: E402
from app.db_models.user import User  # noqa: E402
from app.db_models.review import Review  # noqa: E402
from app.dao import RecipeManagerDAO  # noqa: E402

recipe_dao = RecipeManagerDAO(db)


def test_integration_list_recipes():
    # Esperar un momento si Mongo se está levantando (CI runner)
    for _ in range(10):
        try:
            db.client.admin.command('ping')
            break
        except Exception:
            time.sleep(1)

    client = app.test_client()
    res = client.get('/recipes')
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)


def test_integration_reviews():
    # 1. Crear un usuario de prueba
    user = User(username="Test Critic", email="critic@test.com", role="foodie")
    user_id = recipe_dao.create_user(user)
    assert user_id is not None

    # 2. Crear una receta de prueba
    recipe = Recipe(
        title="Test Tacos",
        ingredients=["tortilla", "carne"],
        tags=["tacos"],
        servings=2,
        author_id=user_id
    )
    recipe_id = recipe_dao.create_recipe(recipe)
    assert recipe_id is not None

    # 3. Publicar una reseña
    review = Review(
        recipe_id=recipe_id,
        user_id=user_id,
        rating=4,
        comment="Very good tacos!"
    )
    review_id = recipe_dao.create_review(review)
    assert review_id is not None

    # 4. Verificar calificación promedio usando el endpoint del API
    client = app.test_client()
    res = client.get(f'/recipes/{recipe_id}')
    assert res.status_code == 200
    recipe_data = res.get_json()
    assert recipe_data['average_rating'] == 4.0
    assert recipe_data['author_name'] == "Test Critic"

    # 5. Publicar otra reseña (5 estrellas)
    review_2 = Review(
        recipe_id=recipe_id,
        user_id=user_id,
        rating=5,
        comment="Amazing the second time!"
    )
    recipe_dao.create_review(review_2)

    # 6. Verificar promedio acumulado (4.5)
    res = client.get(f'/recipes/{recipe_id}')
    assert res.status_code == 200
    recipe_data = res.get_json()
    assert recipe_data['average_rating'] == 4.5
