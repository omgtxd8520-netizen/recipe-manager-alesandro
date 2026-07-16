import os
from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson.objectid import ObjectId

AUTHOR = "Alesandro David Fajardo Torres"

app = Flask(__name__)

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://mongo:27017/recipe_db')
client = MongoClient(MONGO_URI)
db = client.get_default_database()
recipes_col = db.get_collection('recipes')

@app.route('/')
def index():
    return jsonify({"message": "RecipeManager API", "author": AUTHOR})

@app.route('/recipes', methods=['GET'])
def list_recipes():
    q = request.args.get('q')
    if q:
        docs = recipes_col.find({"$text": {"$search": q}})
    else:
        docs = recipes_col.find()
    results = []
    for d in docs:
        d['id'] = str(d.get('_id'))
        d.pop('_id', None)
        results.append(d)
    return jsonify(results)

@app.route('/recipes', methods=['POST'])
def add_recipe():
    payload = request.json
    if not payload:
        return jsonify({"error": "JSON body required"}), 400
    res = recipes_col.insert_one(payload)
    return jsonify({"id": str(res.inserted_id)}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
