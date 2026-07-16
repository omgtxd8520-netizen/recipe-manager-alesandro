import os
import json
from flask import Flask, jsonify, request, abort, send_from_directory
from flask_restx import Api, Resource, fields
from pymongo import MongoClient
from bson.objectid import ObjectId

AUTHOR = "Alesandro David Fajardo Torres"

app = Flask(__name__, static_folder='static', static_url_path='/static')
api = Api(app, version='1.0', title='RecipeManager API', description='API para administrar recetas', doc='/docs')
ns = api.namespace('recipes', description='Operaciones sobre recetas')

# Support using a mock MongoDB for testing (set MONGO_USE_MOCK=1 in env)
if os.environ.get('MONGO_USE_MOCK') == '1':
    import mongomock
    client = mongomock.MongoClient()
else:
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://mongo:27017/recipe_db')
    client = MongoClient(MONGO_URI)

# database and collection
DB_NAME = os.environ.get('MONGO_DB_NAME', 'recipe_db')
db = client[DB_NAME]
recipes_col = db.get_collection('recipes')

# Ensure useful indexes exist on startup (idempotent)
try:
    recipes_col.create_index([('title', 'text'), ('tags', 'text')])
    recipes_col.create_index('ingredients')
except Exception:
    pass

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

        filter_q = {}
        if q:
            filter_q['$text'] = {'$search': q}
        if ingredient:
            filter_q['ingredients'] = {'$in': [ingredient]}
        if tag:
            filter_q['tags'] = {'$in': [tag]}

        docs = recipes_col.find(filter_q)
        results = []
        for d in docs:
            d['id'] = str(d.get('_id'))
            d.pop('_id', None)
            results.append(d)
        return results

    @ns.expect(recipe_model)
    def post(self):
        payload = request.json
        if not payload:
            api.abort(400, 'JSON body required')
        res = recipes_col.insert_one(payload)
        return {'id': str(res.inserted_id)}, 201

@ns.route('/<string:id>')
@ns.response(404, 'Recipe not found')
class Recipe(Resource):
    def get(self, id):
        try:
            _id = ObjectId(id)
        except Exception:
            api.abort(404)
        doc = recipes_col.find_one({'_id': _id})
        if not doc:
            api.abort(404)
        doc['id'] = str(doc.get('_id'))
        doc.pop('_id', None)
        return doc

    @ns.expect(recipe_model)
    def put(self, id):
        try:
            _id = ObjectId(id)
        except Exception:
            api.abort(404)
        payload = request.json
        if not payload:
            api.abort(400, 'JSON body required')
        res = recipes_col.replace_one({'_id': _id}, payload)
        if res.matched_count == 0:
            api.abort(404)
        return {'id': id}

    def delete(self, id):
        try:
            _id = ObjectId(id)
        except Exception:
            api.abort(404)
        res = recipes_col.delete_one({'_id': _id})
        if res.deleted_count == 0:
            api.abort(404)
        return {'deleted': True}

# Serve a minimal frontend
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
