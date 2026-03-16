import pytest
from app import create_app
from app.extensions import db as _db


@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_register(client):
    res = client.post('/register', data={
        'username': 'testuser',
        'email':    'test@example.com',
        'password': 'password123',
    }, follow_redirects=True)
    assert res.status_code == 200


def test_login_wrong_password(client):
    client.post('/register', data={
        'username': 'testuser',
        'email':    'test@example.com',
        'password': 'password123',
    })
    res = client.post('/login', data={
        'username': 'testuser',
        'password': 'wrongpassword',
    }, follow_redirects=True)
    assert 'Sai tài khoản' in res.data.decode('utf-8')
