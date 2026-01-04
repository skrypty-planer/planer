import pytest

from ..src.__init__ import create_app

@pytest.fixture
def client(app):
    return app.test_client()

class UserAuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def me(self, user_id='1'):
        return self._client.get(
            '/auth/me',
            data={'user_id': user_id}
        )

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True
    })

    yield app

@pytest.fixture
def user_auth(client):
    return UserAuthActions(client)
