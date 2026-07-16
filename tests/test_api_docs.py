from app.app import app

def test_docs_available():
    client = app.test_client()
    res = client.get('/docs')
    assert res.status_code == 200
