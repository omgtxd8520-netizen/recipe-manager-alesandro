from app.app import app


def test_index_json():
    client = app.test_client()
    # Solicitar JSON explícitamente para obtener la información de autoría
    res = client.get('/', headers={'Accept': 'application/json'})
    assert res.status_code == 200
    json = res.get_json()
    assert 'author' in json


def test_index_html():
    client = app.test_client()
    # Solicitar por defecto para obtener la UI del RecipeManager
    res = client.get('/')
    assert res.status_code == 200
    assert b'<!doctype html>' in res.data
