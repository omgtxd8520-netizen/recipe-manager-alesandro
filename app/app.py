import os
import sys
from flask import Flask, jsonify, request, send_from_directory
from flask_restx import Api, Resource, fields
from pymongo import MongoClient

# Asegurar que el directorio de la aplicación y la raíz estén en el path para importaciones
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')))

from db_models.recipe import Recipe  # noqa: E402
from db_models.user import User  # noqa: E402
from db_models.review import Review  # noqa: E402
from dao import RecipeManagerDAO  # noqa: E402
from config_vars import MONGO_URI, MONGO_DB_NAME  # noqa: E402
import setup_db  # noqa: E402

AUTHOR = "Alesandro David Fajardo Torres"

app = Flask(__name__, static_folder='static', static_url_path='/static')


# Definir la ruta del frontend ANTES de inicializar Api(app) para evitar colisión de rutas
@app.route('/')
def index():
    """Sirve el frontend interactivo o la metadata JSON según el header de aceptación."""
    best = request.accept_mimetypes.best_match(['text/html', 'application/json'])
    if best == 'application/json' and request.accept_mimetypes[best] > request.accept_mimetypes['text/html']:
        return jsonify({"message": "RecipeManager API", "author": AUTHOR})
    return send_from_directory(app.static_folder, 'index.html')


api = Api(
    app,
    version='1.0',
    title='RecipeManager API',
    description='API para administrar recetas, autores y reseñas',
    doc='/docs'
)
ns = api.namespace('recipes', description='Operaciones sobre recetas')
ns_users = api.namespace('users', description='Operaciones sobre usuarios')
ns_reviews = api.namespace('reviews', description='Operaciones sobre reseñas y calificaciones')

# Soporte para usar mock MongoDB en tests (estableciendo MONGO_USE_MOCK=1)
if os.environ.get('MONGO_USE_MOCK') == '1':
    import mongomock
    client = mongomock.MongoClient()
    db = client[MONGO_DB_NAME]
else:
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    try:
        setup_db.setup()
    except Exception:
        pass

recipes_col = db.get_collection('recipes')

# Instanciar el DAO unificado (RecipeManagerDAO)
recipe_dao = RecipeManagerDAO(db)

# Modelos Swagger
user_model = api.model('User', {
    'username': fields.String(required=True, description='Nombre de usuario'),
    'email': fields.String(required=True, description='Correo electrónico'),
    'role': fields.String(description='Rol del usuario (chef, foodie, admin)')
})

review_model = api.model('Review', {
    'recipe_id': fields.String(required=True, description='ID de la receta valorada'),
    'user_id': fields.String(required=True, description='ID del usuario que valora'),
    'rating': fields.Integer(required=True, description='Calificación de 1 a 5 estrellas'),
    'comment': fields.String(description='Comentario u opinión')
})

recipe_model = api.model('Recipe', {
    'title': fields.String(required=True, description='Título de la receta'),
    'ingredients': fields.List(fields.String, description='Lista de ingredientes'),
    'tags': fields.List(fields.String, description='Tags/etiquetas'),
    'servings': fields.Integer(description='Porciones'),
    'author_id': fields.String(description='ID del autor de la receta')
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
            d['average_rating'] = recipe_dao.get_recipe_average_rating(r.id)
            if r.author_id:
                author = recipe_dao.get_user(r.author_id)
                d['author_name'] = author.username if author else "Desconocido"
            else:
                d['author_name'] = "Desconocido"
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
        d['average_rating'] = recipe_dao.get_recipe_average_rating(recipe.id)
        if recipe.author_id:
            author = recipe_dao.get_user(recipe.author_id)
            d['author_name'] = author.username if author else "Desconocido"
        else:
            d['author_name'] = "Desconocido"
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


@ns_users.route('')
class UserList(Resource):
    def get(self):
        users = recipe_dao.list_users()
        results = []
        for u in users:
            d = u.to_dict()
            d['id'] = u.id
            results.append(d)
        return results

    @ns_users.expect(user_model)
    def post(self):
        payload = request.json
        if not payload:
            api.abort(400, 'JSON body required')
        user = User.from_dict(payload)
        new_id = recipe_dao.create_user(user)
        return {'id': new_id}, 201


@ns_reviews.route('')
class ReviewCreate(Resource):
    @ns_reviews.expect(review_model)
    def post(self):
        payload = request.json
        if not payload:
            api.abort(400, 'JSON body required')
        review = Review.from_dict(payload)
        recipe = recipe_dao.get_recipe(review.recipe_id)
        if not recipe:
            api.abort(404, 'Recipe not found')
        user = recipe_dao.get_user(review.user_id)
        if not user:
            api.abort(404, 'User not found')
        new_id = recipe_dao.create_review(review)
        return {'id': new_id}, 201


@ns_reviews.route('/recipe/<string:recipe_id>')
@ns_reviews.response(404, 'Recipe not found')
class RecipeReviewList(Resource):
    def get(self, recipe_id):
        recipe = recipe_dao.get_recipe(recipe_id)
        if not recipe:
            api.abort(404, 'Recipe not found')
        reviews = recipe_dao.list_reviews_by_recipe(recipe_id)
        results = []
        for r in reviews:
            d = r.to_dict()
            d['id'] = r.id
            user = recipe_dao.get_user(r.user_id)
            d['username'] = user.username if user else "Usuario eliminado"
            results.append(d)
        return results


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
