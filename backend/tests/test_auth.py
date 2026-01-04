import pytest
from flask import g, session, jsonify
from ..src.error_handling.logger import logger
from .__init__ import client, app

def test_login(client, app):
    response = client.post(
        '/auth/login', json={'username': 'test', 'password': 'test123'}
    )
    assert response.status_code == 200

    # with app.app_context():
    #     assert get_db().execute(
    #         "SELECT * FROM user WHERE username = 'a'",
    #     ).fetchone() is not None


@pytest.mark.parametrize(('username', 'password', 'status_code'), (
    ('', '', 400),
    ('a', '', 400),
    ('test', 'test123', 200),
))
def test_login_validate_input(client, username, password, status_code):
    response = client.post(
        '/auth/login',
        json={'username': username, 'password': password}
    )
    assert status_code == response.status_code


def test_me(client, app):
    response = client.get(
        '/auth/me',
        json={'user_id': 1}
    )
    assert response.status_code == 200
    
    # with app.app_context():
    #     assert get_db().execute(
    #         "SELECT * FROM user WHERE user_id = 1",
    #     ).fetchone() is not None

@pytest.mark.parametrize(('user_id', 'status_code'), (
    ('', 400),
    ('a', 400),
    (1, 200),
))
def test_me_validate_input(client, user_id, status_code):
    response = client.get(
        '/auth/me',
        json={'user_id': user_id}
    )
    assert status_code == response.status_code