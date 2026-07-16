from pymongo.database import Database
from bson import ObjectId
from db_models.recipe import Recipe
from db_models.user import User
from db_models.review import Review


class RecipeManagerDAO:
    """
    Capa de Acceso a Datos (DAO) para las colecciones 'recipes', 'users'
    y 'reviews' en MongoDB. Todo el resto de la app (la API Flask) pasa
    siempre por acá en lugar de tocar pymongo directamente.

    Uso:
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB_NAME]
        dao = RecipeManagerDAO(db)
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
        """
        Lista recetas con filtros opcionales combinables (AND):
        - q: texto libre sobre título/tags (usa el índice de texto de setup_db.py)
        - ingredient: ingrediente exacto que la receta debe contener
        - tag: etiqueta exacta

        >>> dao.list_recipes(q="pollo", tag="rápido")
        >>> dao.list_recipes(ingredient="ajo")
        """
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
        """
        Busca una receta por ObjectId. None si no existe o el id es inválido.

        >>> dao.get_recipe("64f1a2b3c4d5e6f7a8b9c0d1")
        """
        try:
            _id = ObjectId(recipe_id)
        except Exception:
            return None
        doc = self._recipes.find_one({'_id': _id})
        return Recipe.from_dict(doc) if doc else None

    def create_recipe(self, recipe: Recipe) -> str:
        """
        Inserta una receta y devuelve el id generado por MongoDB.

        >>> dao.create_recipe(Recipe(title="Pasta al ajo", ingredients=["pasta", "ajo"]))
        """
        res = self._recipes.insert_one(recipe.to_dict())
        return str(res.inserted_id)

    def update_recipe(self, recipe_id: str, recipe: Recipe) -> bool:
        """
        Reemplaza una receta existente. True si el id existía y se actualizó.

        >>> dao.update_recipe(receta_id, receta_editada)
        """
        try:
            _id = ObjectId(recipe_id)
        except Exception:
            return False
        res = self._recipes.replace_one({'_id': _id}, recipe.to_dict())
        return res.matched_count > 0

    def delete_recipe(self, recipe_id: str) -> bool:
        """
        Elimina una receta y, en cascada, sus reseñas asociadas para no
        dejar reseñas huérfanas apuntando a una receta borrada.

        >>> dao.delete_recipe(receta_id)
        """
        try:
            _id = ObjectId(recipe_id)
        except Exception:
            return False
        self._reviews.delete_many({"recipe_id": recipe_id})
        res = self._recipes.delete_one({'_id': _id})
        return res.deleted_count > 0

    # -------------------------------------------------------------
    # Operaciones: Users (Usuarios)
    # -------------------------------------------------------------
    def list_users(self) -> list[User]:
        """Devuelve todos los usuarios (chefs, foodies y admins) registrados."""
        docs = self._users.find()
        return [User.from_dict(d) for d in docs]

    def get_user(self, user_id: str) -> User | None:
        """Busca un usuario por id. None si no existe o el id es inválido."""
        try:
            _id = ObjectId(user_id)
        except Exception:
            return None
        doc = self._users.find_one({'_id': _id})
        return User.from_dict(doc) if doc else None

    def create_user(self, user: User) -> str:
        """
        Inserta un usuario nuevo y devuelve el id generado.

        >>> dao.create_user(User(username="Jamie Oliver", email="jamie@foodies.com", role="chef"))
        """
        res = self._users.insert_one(user.to_dict())
        return str(res.inserted_id)

    def delete_user(self, user_id: str) -> bool:
        """Elimina un usuario por id. True si existía y se borró."""
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
        """Reseñas de una receta, de la más reciente a la más antigua."""
        docs = self._reviews.find({"recipe_id": recipe_id}).sort("created_at", -1)
        return [Review.from_dict(d) for d in docs]

    def create_review(self, review: Review) -> str:
        """
        Inserta una reseña y devuelve el id generado.

        >>> dao.create_review(Review(recipe_id=rid, user_id=uid, rating=5, comment="Buenísima"))
        """
        res = self._reviews.insert_one(review.to_dict())
        return str(res.inserted_id)

    def get_recipe_average_rating(self, recipe_id: str) -> float:
        """
        Promedio de calificación (1-5) de una receta a partir de sus
        reseñas. 0.0 si todavía no tiene ninguna. Se calcula con un
        pipeline de agregación ($match + $group) en vez de traer todas
        las reseñas y promediar en Python.
        """
        pipeline = [
            {"$match": {"recipe_id": recipe_id}},
            {"$group": {"_id": "$recipe_id", "avg_rating": {"$avg": "$rating"}}}
        ]
        res = list(self._reviews.aggregate(pipeline))
        if res:
            return round(res[0]["avg_rating"], 1)
        return 0.0
