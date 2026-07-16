from app.app import app

def test_index():
    client = app.test_client()
    res = client.get('/')
    assert res.status_code == 200
    json = res.get_json()
    assert 'author' in json
