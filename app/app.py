import os
import sys
from flask import Flask, jsonify, request, send_from_directory
from flask_restx import Api, Resource, fields
from pymongo import MongoClient

# Asegurar que el directorio de la aplicación esté en el path para importaciones limpias
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db_models.recipe import Recipe  # noqa: E402
from dao import RecipeDAO  # noqa: E402

AUTHOR = "Alesandro David Fajardo Torres"

app = Flask(__name__, static_folder='static', static_url_path='/static')


# Definir la ruta del frontend ANTES de inicializar Api(app) para evitar colisión de rutas
@app.route('/')
def index():
    """Sirve el frontend interactivo o la metadata JSON según el header de aceptación."""
    # Retorna JSON si se solicita explícitamente, de lo contrario sirve el HTML
    best = request.accept_mimetypes.best_match(['text/html', 'application/json'])
    if best == 'application/json' and request.accept_mimetypes[best] > request.accept_mimetypes['text/html']:
        return jsonify({"message": "RecipeManager API", "author": AUTHOR})
    return send_from_directory(app.static_folder, 'index.html')


api = Api(app, version='1.0', title='RecipeManager API', description='API para administrar recetas', doc='/docs')
ns = api.namespace('recipes', description='Operaciones sobre recetas')

# Soporte para usar mock MongoDB en tests (estableciendo MONGO_USE_MOCK=1)
if os.environ.get('MONGO_USE_MOCK') == '1':
    import mongomock
    client = mongomock.MongoClient()
else:
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://mongo:27017/recipe_db')
    client = MongoClient(MONGO_URI)

# Conexión a la base de datos y la colección
DB_NAME = os.environ.get('MONGO_DB_NAME', 'recipe_db')
db = client[DB_NAME]
recipes_col = db.get_collection('recipes')

# Asegurar la creación de índices al arrancar de forma idempotente
try:
    recipes_col.create_index([('title', 'text'), ('tags', 'text')])
    recipes_col.create_index('ingredients')
except Exception:
    pass

# Instanciar el objeto DAO de acceso a datos
recipe_dao = RecipeDAO(recipes_col)

recipe_model = api.model('Recipe', {
    'title': fields.String(required=True, description='Título de la receta'),
    'ingredients': fields.List(fields.String, description='Lista de ingredientes'),
    'tags': fields.List(fields.String, description='Tags/etiquetas'),
    'servings': fields.Integer(description='Porciones')
})


@ns.route('')
class RecipeList(Resource):
    @ns.doc(params={'q': 'Búsqueda de texto', 'ingredient': 'Filtrar por ingrediente', 'tag': 'Filtrar por tag'})
    def get(self):
        q = request.args.get('q')
        ingredient = request.args.get('ingredient')
        tag = request.args.get('tag')

        recipes = recipe_dao.list_recipes(q=q, ingredient=ingredient, tag=tag)
        results = []
        for r in recipes:
            d = r.to_dict()
            d['id'] = r.id
            results.append(d)
        return results

    @ns.expect(recipe_model)
    def post(self):
        payload = request.json
        if not payload:
            api.abort(400, 'JSON body required')
        recipe = Recipe.from_dict(payload)
        new_id = recipe_dao.create_recipe(recipe)
        return {'id': new_id}, 201


@ns.route('/<string:id>')
@ns.response(404, 'Recipe not found')
class RecipeResource(Resource):
    def get(self, id):
        recipe = recipe_dao.get_recipe(id)
        if not recipe:
            api.abort(404)
        d = recipe.to_dict()
        d['id'] = recipe.id
        return d

    @ns.expect(recipe_model)
    def put(self, id):
        payload = request.json
        if not payload:
            api.abort(400, 'JSON body required')
        recipe = Recipe.from_dict(payload)
        success = recipe_dao.update_recipe(id, recipe)
        if not success:
            api.abort(404)
        return {'id': id}

    def delete(self, id):
        success = recipe_dao.delete_recipe(id)
        if not success:
            api.abort(404)
        return {'deleted': True}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
