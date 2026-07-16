from pymongo.database import Database
from bson import ObjectId
from db_models.recipe import Recipe
from db_models.user import User
from db_models.review import Review


class RecipeManagerDAO:
    """
    Capa de Acceso a Datos (DAO) unificada para administrar las colecciones
    'recipes', 'users' y 'reviews' en MongoDB.

    Abstrae todas las operaciones físicas sobre MongoDB en métodos con
    semántica del dominio culinario (buscar por ingrediente, calificar
    una receta, listar reseñas). El resto de la aplicación (la API Flask)
    nunca construye queries de MongoDB directamente — siempre pasa por
    esta clase.

    Ejemplo
    -------
    from pymongo import MongoClient
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
        Obtiene la lista de recetas aplicando filtros opcionales.

        Los tres filtros son combinables entre sí (AND lógico). Si no se
        pasa ninguno, devuelve el catálogo completo.

        Parámetros
        ----------
        q          : búsqueda de texto libre sobre título y tags (usa el
                     índice de texto creado en setup_db.py)
        ingredient : filtra recetas que contengan este ingrediente exacto
        tag        : filtra recetas que tengan esta etiqueta

        Ejemplo
        -------
        # Todas las recetas que mencionen "pollo" y estén etiquetadas "rápido"
        recetas = dao.list_recipes(q="pollo", tag="rápido")

        # Recetas que usan ajo
        recetas = dao.list_recipes(ingredient="ajo")
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
        Busca una receta por su ObjectId.
        Devuelve None si el id no existe o no es un ObjectId válido.

        Ejemplo
        -------
        receta = dao.get_recipe("64f1a2b3c4d5e6f7a8b9c0d1")
        if receta:
            print(receta.title)
        """
        try:
            _id = ObjectId(recipe_id)
        except Exception:
            return None
        doc = self._recipes.find_one({'_id': _id})
        return Recipe.from_dict(doc) if doc else None

    def create_recipe(self, recipe: Recipe) -> str:
        """
        Inserta una receta nueva. Devuelve el id generado por MongoDB.

        Ejemplo
        -------
        receta = Recipe(
            title="Pasta al ajo",
            ingredients=["pasta", "ajo", "aceite", "perejil"],
            tags=["pasta", "almuerzo"],
            servings=3,
            author_id=autor_id,
        )
        receta_id = dao.create_recipe(receta)
        """
        res = self._recipes.insert_one(recipe.to_dict())
        return str(res.inserted_id)

    def update_recipe(self, recipe_id: str, recipe: Recipe) -> bool:
        """
        Reemplaza una receta existente por su ID.
        Devuelve True si se encontró y actualizó, False si el id no existe.

        Ejemplo
        -------
        actualizada = dao.update_recipe(receta_id, receta_editada)
        """
        try:
            _id = ObjectId(recipe_id)
        except Exception:
            return False
        res = self._recipes.replace_one({'_id': _id}, recipe.to_dict())
        return res.matched_count > 0

    def delete_recipe(self, recipe_id: str) -> bool:
        """
        Elimina una receta por su ID y, en cascada, todas sus reseñas
        asociadas (evita reseñas huérfanas apuntando a una receta borrada).
        Devuelve True si la receta existía y fue eliminada.

        Ejemplo
        -------
        borrada = dao.delete_recipe(receta_id)
        """
        try:
            _id = ObjectId(recipe_id)
        except Exception:
            return False
        # Eliminar las reseñas asociadas antes de borrar la receta
        self._reviews.delete_many({"recipe_id": recipe_id})
        res = self._recipes.delete_one({'_id': _id})
        return res.deleted_count > 0

    # -------------------------------------------------------------
    # Operaciones: Users (Usuarios)
    # -------------------------------------------------------------
    def list_users(self) -> list[User]:
        """
        Obtiene todos los usuarios registrados (chefs, foodies y admins).

        Ejemplo
        -------
        usuarios = dao.list_users()
        """
        docs = self._users.find()
        return [User.from_dict(d) for d in docs]

    def get_user(self, user_id: str) -> User | None:
        """
        Busca un usuario por su ID.
        Devuelve None si el id no existe o no es un ObjectId válido.

        Ejemplo
        -------
        usuario = dao.get_user(autor_id)
        """
        try:
            _id = ObjectId(user_id)
        except Exception:
            return None
        doc = self._users.find_one({'_id': _id})
        return User.from_dict(doc) if doc else None

    def create_user(self, user: User) -> str:
        """
        Inserta un nuevo usuario. Devuelve el id generado por MongoDB.

        Ejemplo
        -------
        usuario = User(username="Jamie Oliver", email="jamie@foodies.com", role="chef")
        usuario_id = dao.create_user(usuario)
        """
        res = self._users.insert_one(user.to_dict())
        return str(res.inserted_id)

    def delete_user(self, user_id: str) -> bool:
        """
        Elimina un usuario por su ID.
        Devuelve True si el usuario existía y fue eliminado.

        Ejemplo
        -------
        borrado = dao.delete_user(usuario_id)
        """
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
        """
        Lista todas las reseñas de una receta, de la más reciente a la
        más antigua.

        Ejemplo
        -------
        reseñas = dao.list_reviews_by_recipe(receta_id)
        for r in reseñas:
            print(r.rating, r.comment)
        """
        docs = self._reviews.find({"recipe_id": recipe_id}).sort("created_at", -1)
        return [Review.from_dict(d) for d in docs]

    def create_review(self, review: Review) -> str:
        """
        Inserta una reseña para una receta. Devuelve el id generado.

        Ejemplo
        -------
        reseña = Review(
            recipe_id=receta_id,
            user_id=usuario_id,
            rating=5,
            comment="Quedó espectacular, la volvería a hacer.",
        )
        reseña_id = dao.create_review(reseña)
        """
        res = self._reviews.insert_one(review.to_dict())
        return str(res.inserted_id)

    def get_recipe_average_rating(self, recipe_id: str) -> float:
        """
        Calcula el promedio de calificación (1 a 5 estrellas) de una
        receta a partir de todas sus reseñas. Devuelve 0.0 si la receta
        no tiene reseñas todavía.

        Usa un pipeline de agregación de MongoDB ($match + $group) en
        lugar de traer todas las reseñas y promediar en Python — más
        eficiente cuando una receta tiene muchas reseñas.

        Ejemplo
        -------
        promedio = dao.get_recipe_average_rating(receta_id)
        # 4.7
        """
        pipeline = [
            {"$match": {"recipe_id": recipe_id}},
            {"$group": {"_id": "$recipe_id", "avg_rating": {"$avg": "$rating"}}}
        ]
        res = list(self._reviews.aggregate(pipeline))
        if res:
            return round(res[0]["avg_rating"], 1)
        return 0.0
