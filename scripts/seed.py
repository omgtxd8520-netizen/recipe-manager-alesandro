import os
import sys
from pymongo import MongoClient

# Ajustar paths para importar desde el módulo del app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))

from app.db_models.user import User  # noqa: E402
from app.db_models.recipe import Recipe  # noqa: E402
from app.db_models.review import Review  # noqa: E402
from app.dao import RecipeManagerDAO  # noqa: E402

from config_vars import MONGO_URI, MONGO_DB_NAME  # noqa: E402
import setup_db  # noqa: E402

client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]

# Instanciar el DAO unificado
recipe_dao = RecipeManagerDAO(db)


def seed():
    print("[Semillero] Purgando base de datos...")
    db["recipes"].delete_many({})
    db["users"].delete_many({})
    db["reviews"].delete_many({})

    # 1. Crear Usuarios (Chefs y Críticos)
    print("[Semillero] Creando usuarios...")
    user_data = [
        User(username="Gordon Ramsay", email="gordon@hellskitchen.com", role="chef"),
        User(username="Jamie Oliver", email="jamie@foodies.com", role="chef"),
        User(username="Gaston Acurio", email="gaston@astridygaston.com", role="chef"),
        User(username="Critico Gourmet", email="critico@michelin.com", role="foodie"),
        User(username="David Fajardo", email="david.fajardo@estudiante.com", role="foodie")
    ]

    users = {}
    for u in user_data:
        uid = recipe_dao.create_user(u)
        users[u.username] = uid
        print(f"  Usuario creado: {u.username} (ID: {uid})")

    # 2. Crear Recetas asociadas a los Chefs
    print("[Semillero] Creando recetas...")
    recipe_data = [
        Recipe(
            title="Beef Wellington",
            ingredients=["lomo de res", "champiñones", "hojaldre", "mostaza", "jamón serrano"],
            tags=["exclusivo", "horno", "británico"],
            servings=4,
            author_id=users["Gordon Ramsay"]
        ),
        Recipe(
            title="Ceviche Clásico Peruano",
            ingredients=["pescado fresco", "limón", "cebolla morada", "ají limo", "cilantro"],
            tags=["marisco", "fresco", "peruano"],
            servings=2,
            author_id=users["Gaston Acurio"]
        ),
        Recipe(
            title="Pasta Pesto Rápida",
            ingredients=["pasta", "albahaca", "piñones", "ajo", "queso parmesano", "aceite de oliva"],
            tags=["italiano", "rápido", "vegetariano"],
            servings=3,
            author_id=users["Jamie Oliver"]
        ),
        Recipe(
            title="Tarta de Chocolate Lava",
            ingredients=["chocolate amargo", "mantequilla", "huevos", "azúcar", "harina"],
            tags=["postre", "dulce", "horno"],
            servings=2,
            author_id=users["Gordon Ramsay"]
        ),
        Recipe(
            title="Causa Limeña",
            ingredients=["papa amarilla", "ají amarillo", "limón", "pollo deshilachado", "mayonesa"],
            tags=["entrada", "frío", "peruano"],
            servings=4,
            author_id=users["Gaston Acurio"]
        )
    ]

    recipes = {}
    for r in recipe_data:
        rid = recipe_dao.create_recipe(r)
        recipes[r.title] = rid
        print(f"  Receta creada: {r.title} (ID: {rid})")

    # 3. Crear Reseñas y Calificaciones
    print("[Semillero] Creando reseñas de los usuarios...")
    review_data = [
        # Beef Wellington
        Review(
            recipe_id=recipes["Beef Wellington"],
            user_id=users["Critico Gourmet"],
            rating=5,
            comment="Una obra de arte absoluta. La cocción perfecta del lomo y el hojaldre crujiente."
        ),
        Review(
            recipe_id=recipes["Beef Wellington"],
            user_id=users["David Fajardo"],
            rating=4,
            comment="Exquisito pero requiere mucha técnica. Salió genial."
        ),
        # Ceviche Peruano
        Review(
            recipe_id=recipes["Ceviche Clásico Peruano"],
            user_id=users["Critico Gourmet"],
            rating=5,
            comment="El equilibrio perfecto de acidez y frescura. Increíble."
        ),
        Review(
            recipe_id=recipes["Ceviche Clásico Peruano"],
            user_id=users["Jamie Oliver"],
            rating=5,
            comment="Fresco, vibrante, me encanta la combinación cítrica."
        ),
        Review(
            recipe_id=recipes["Ceviche Clásico Peruano"],
            user_id=users["David Fajardo"],
            rating=5,
            comment="Mi favorito de siempre. Muy fácil de seguir."
        ),
        # Pasta Pesto Rápida
        Review(
            recipe_id=recipes["Pasta Pesto Rápida"],
            user_id=users["Gordon Ramsay"],
            rating=3,
            comment="Rápido, sí. Pero le falta un toque de sazón y más intensidad de ajo."
        ),
        Review(
            recipe_id=recipes["Pasta Pesto Rápida"],
            user_id=users["Critico Gourmet"],
            rating=4,
            comment="Ideal para una cena rápida entre semana, simple y sabroso."
        ),
        # Tarta de Chocolate
        Review(
            recipe_id=recipes["Tarta de Chocolate Lava"],
            user_id=users["David Fajardo"],
            rating=5,
            comment="¡El volcán de chocolate se derrite a la perfección! Un éxito total."
        ),
        Review(
            recipe_id=recipes["Tarta de Chocolate Lava"],
            user_id=users["Gaston Acurio"],
            rating=4,
            comment="Buen uso del cacao, postre fantástico."
        )
    ]

    for rev in review_data:
        recipe_dao.create_review(rev)
        print(f"  Reseña creada para receta {rev.recipe_id} (Calificación: {rev.rating}★)")

    # 4. Configurar índices de texto y campo utilizando setup_db
    setup_db.setup()

    print("\n[Semillero] Base de datos sembrada con éxito en esquema multi-colección relacional.")


if __name__ == "__main__":
    seed()
