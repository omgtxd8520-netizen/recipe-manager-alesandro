from pymongo.collection import Collection
from bson import ObjectId
from db_models.recipe import Recipe


class RecipeDAO:
    """
    Capa de Acceso a Datos (DAO) para administrar las recetas en MongoDB.
    Encapsula todas las consultas físicas de PyMongo.
    """
    def __init__(self, collection: Collection):
        self._collection = collection

    def list_recipes(self, q: str = None, ingredient: str = None, tag: str = None) -> list[Recipe]:
        """Obtiene la lista de recetas aplicando filtros opcionales de búsqueda o categorías."""
        filter_q = {}
        if q:
            filter_q['$text'] = {'$search': q}
        if ingredient:
            filter_q['ingredients'] = {'$in': [ingredient]}
        if tag:
            filter_q['tags'] = {'$in': [tag]}

        docs = self._collection.find(filter_q)
        return [Recipe.from_dict(d) for d in docs]

    def get_recipe(self, recipe_id: str) -> Recipe | None:
        """Busca una receta por su ObjectId. Retorna None si no existe o el formato es incorrecto."""
        try:
            _id = ObjectId(recipe_id)
        except Exception:
            return None
        doc = self._collection.find_one({'_id': _id})
        return Recipe.from_dict(doc) if doc else None

    def create_recipe(self, recipe: Recipe) -> str:
        """Inserta una nueva receta. Retorna el ID de la receta creada."""
        res = self._collection.insert_one(recipe.to_dict())
        return str(res.inserted_id)

    def update_recipe(self, recipe_id: str, recipe: Recipe) -> bool:
        """Reemplaza una receta existente por su ID. Retorna True si se modificó exitosamente."""
        try:
            _id = ObjectId(recipe_id)
        except Exception:
            return False
        res = self._collection.replace_one({'_id': _id}, recipe.to_dict())
        return res.matched_count > 0

    def delete_recipe(self, recipe_id: str) -> bool:
        """Elimina una receta por su ID. Retorna True si la eliminación fue exitosa."""
        try:
            _id = ObjectId(recipe_id)
        except Exception:
            return False
        res = self._collection.delete_one({'_id': _id})
        return res.deleted_count > 0
