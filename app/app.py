import os
import json
from flask import Flask, jsonify, request, abort
from pymongo import MongoClient
from bson.objectid import ObjectId

AUTHOR = "Alesandro David Fajardo Torres"

app = Flask(__name__)

# Support using a mock MongoDB for testing (set MONGO_USE_MOCK=1 in env)
if os.environ.get('MONGO_USE_MOCK') == '1':
    try:
        import mongomock
n    except Exception:
        raise
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
    # index creation may fail in some hosted Mongo services, ignore
    pass

@app.route('/')
def index():
    return jsonify({"message": "RecipeManager API", "author": AUTHOR})

@app.route('/recipes', methods=['GET'])
def list_recipes():
    # filters: q (text search), ingredient, tag
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
    return jsonify(results)

@app.route('/recipes/<id>', methods=['GET'])
def get_recipe(id):
    try:
        _id = ObjectId(id)
    except Exception:
        abort(404)
    doc = recipes_col.find_one({'_id': _id})
    if not doc:
        abort(404)
    doc['id'] = str(doc.get('_id'))
    doc.pop('_id', None)
    return jsonify(doc)

@app.route('/recipes', methods=['POST'])
def add_recipe():
    payload = request.json
    if not payload:
        return jsonify({"error": "JSON body required"}), 400
    res = recipes_col.insert_one(payload)
    return jsonify({"id": str(res.inserted_id)}), 201

@app.route('/recipes/<id>', methods=['PUT'])
def update_recipe(id):
    try:
        _id = ObjectId(id)
    except Exception:
        abort(404)
    payload = request.json
    if not payload:
        return jsonify({"error": "JSON body required"}), 400
    res = recipes_col.replace_one({'_id': _id}, payload)
    if res.matched_count == 0:
        abort(404)
    return jsonify({"id": id})

@app.route('/recipes/<id>', methods=['DELETE'])
def delete_recipe(id):
    try:
        _id = ObjectId(id)
    except Exception:
        abort(404)
    res = recipes_col.delete_one({'_id': _id})
    if res.deleted_count == 0:
        abort(404)
    return jsonify({"deleted": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
