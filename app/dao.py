from pymongo.database import Database
from bson import ObjectId
from db_models.recipe import Recipe
from db_models.user import User
from db_models.review import Review


class RecipeManagerDAO:
    """
    Capa de Acceso a Datos (DAO) unificada para administrar las colecciones
    'recipes', 'users' y 'reviews' en MongoDB.
    Abstrae todas las operaciones físicas sobre MongoDB.
    """
    def __init__(self, db: Database):
        self._db = db
        self._recipes = db["recipes"]
        self._users = db["users"]
        self._reviews = db["reviews"]

    # -------------------------------------------------------------
    # Operaciones: Recipes (Recetas)
    # -------------------------------------------------------------
    def list_recipes(self, q: str = None, ingredient: str = None, tag: str = None) -> list[Recipe]:
        """Obtiene la lista de recetas aplicando filtros opcionales."""
        filter_q = {}
        if q:
            filter_q['$text'] = {'$search': q}
        if ingredient:
            filter_q['ingredients'] = {'$in': [ingredient]}
        if tag:
            filter_q['tags'] = {'$in': [tag]}

        docs = self._recipes.find(filter_q)
        return [Recipe.from_dict(d) for d in docs]

    def get_recipe(self, recipe_id: str) -> Recipe | None:
        """Busca una receta por su ObjectId."""
        try:
            _id = ObjectId(recipe_id)
        except Exception:
            return None
        doc = self._recipes.find_one({'_id': _id})
        return Recipe.from_dict(doc) if doc else None

    def create_recipe(self, recipe: Recipe) -> str:
        """Inserta una receta. Retorna el ID generado."""
        res = self._recipes.insert_one(recipe.to_dict())
        return str(res.inserted_id)

    def update_recipe(self, recipe_id: str, recipe: Recipe) -> bool:
        """Reemplaza una receta existente por su ID."""
        try:
            _id = ObjectId(recipe_id)
        except Exception:
            return False
        res = self._recipes.replace_one({'_id': _id}, recipe.to_dict())
        return res.matched_count > 0

    def delete_recipe(self, recipe_id: str) -> bool:
        """Elimina una receta por su ID. También elimina sus reseñas asociadas."""
        try:
            _id = ObjectId(recipe_id)
        except Exception:
            return False
        # Eliminar las reseñas asociadas
        self._reviews.delete_many({"recipe_id": recipe_id})
        res = self._recipes.delete_one({'_id': _id})
        return res.deleted_count > 0

    # -------------------------------------------------------------
    # Operaciones: Users (Usuarios)
    # -------------------------------------------------------------
    def list_users(self) -> list[User]:
        """Obtiene todos los usuarios registrados."""
        docs = self._users.find()
        return [User.from_dict(d) for d in docs]

    def get_user(self, user_id: str) -> User | None:
        """Busca un usuario por su ID."""
        try:
            _id = ObjectId(user_id)
        except Exception:
            return None
        doc = self._users.find_one({'_id': _id})
        return User.from_dict(doc) if doc else None

    def create_user(self, user: User) -> str:
        """Inserta un nuevo usuario."""
        res = self._users.insert_one(user.to_dict())
        return str(res.inserted_id)

    def delete_user(self, user_id: str) -> bool:
        """Elimina un usuario por su ID."""
        try:
            _id = ObjectId(user_id)
        except Exception:
            return False
        res = self._users.delete_one({'_id': _id})
        return res.deleted_count > 0

    # -------------------------------------------------------------
    # Operaciones: Reviews (Reseñas / Calificaciones)
    # -------------------------------------------------------------
    def list_reviews_by_recipe(self, recipe_id: str) -> list[Review]:
        """Lista todas las reseñas hechas a una receta específica, ordenadas por fecha."""
        docs = self._reviews.find({"recipe_id": recipe_id}).sort("created_at", -1)
        return [Review.from_dict(d) for d in docs]

    def create_review(self, review: Review) -> str:
        """Inserta una reseña para una receta."""
        res = self._reviews.insert_one(review.to_dict())
        return str(res.inserted_id)

    def get_recipe_average_rating(self, recipe_id: str) -> float:
        """Calcula el promedio de calificación para una receta. Retorna 0.0 si no tiene reseñas."""
        pipeline = [
            {"$match": {"recipe_id": recipe_id}},
            {"$group": {"_id": "$recipe_id", "avg_rating": {"$avg": "$rating"}}}
        ]
        res = list(self._reviews.aggregate(pipeline))
        if res:
            return round(res[0]["avg_rating"], 1)
        return 0.0
