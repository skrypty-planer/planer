import pytest
from flask import g, session, Flask, current_app
from flask.testing import FlaskClient
from .__init__ import AuthManager, CacheManager
from .conftests import app, client, auth, cache

def test_check_if_user_is_logged_in(app: Flask, client: FlaskClient, auth: AuthManager):
    with app.test_request_context():
        assert not auth.check_if_user_is_logged_in( 'test' )
    
    with client:
        register_res = client.post(
            '/auth/register',
            json={'username': 'test', 'password': 'zaq1@WSX'}
        )
        assert register_res.status_code == 200
        assert auth.check_if_user_is_logged_in( register_res.json['user']['id'] )

def test_check_if_user_exists(client: FlaskClient, auth: AuthManager):
    assert not auth.check_if_user_exists( 'test' )
    
    with client:
        register_res = client.post(
            '/auth/register',
            json={'username': 'test', 'password': 'zaq1@WSX'}
        )
        assert register_res.status_code == 200
        assert auth.check_if_user_exists( register_res.json['user']['id'] )

def test_login(app: Flask, client: FlaskClient, auth: AuthManager):
    with app.test_request_context():
        assert not auth.check_if_user_is_logged_in( 'test' )
    
    with client:
        register_res = client.post(
            '/auth/register',
            json={'username': 'test', 'password': 'zaq1@WSX'}
        )
        assert register_res.status_code == 200

        logout_res = client.post(
            '/auth/logout'
        )
        assert logout_res.status_code == 200

        login_res = client.post(
            '/auth/login',
            json={'username': 'test', 'password': 'zaq1@WSX'}
        )
        assert login_res.status_code == 200
        assert auth.check_if_user_is_logged_in( register_res.json['user']['id'] )

def test_validate_password(auth: AuthManager):
    status, message = auth.validate_password('zaq1@WSX')
    assert status == True
    assert message == None
    
    status, message = auth.validate_password('z')
    assert status == False
    assert message == 'Hasło musi mieć co najmniej 8 znaków'

    status, message = auth.validate_password('zaq1@wsx')
    assert status == False
    assert message == 'Hasło musi zawierać co najmniej jedną dużą literę'

    status, message = auth.validate_password('zaq@WSXz')
    assert status == False
    assert message == 'Hasło musi zawierać co najmniej jedną cyfrę'

    status, message = auth.validate_password('zaq1WSXz')
    assert status == False
    assert message == 'Hasło musi zawierać co najmniej jeden znak specjalny'   

def test_generate_avatar(auth: AuthManager):
    avatar = auth.generate_avatar('test')
    assert avatar is not None
    assert '<text x="50" y="50" dy=".35em" font-size="50" font-family="Arial, sans-serif" font-weight="bold" text-anchor="middle" fill="white">T</text>'

def test_register_user(app: Flask, client: FlaskClient, auth: AuthManager, cache: CacheManager):
    with app.test_request_context():
        assert not auth.check_if_user_exists( 'test1' )
    
    with client:
        test1_user_id, message = auth.register_user('test1', 'zaq1@WSX')
        assert test1_user_id is not None
        assert message is None
        assert test1_user_id in cache.cache.get("users")

        user_id, message = auth.register_user('test1', 'zaq1@WSX')
        assert user_id is None
        assert message == 'Użytkownik o tej nazwie już istnieje'
        assert test1_user_id in cache.cache.get("users")

        user_id, message = auth.register_user('test2', 'piwo')
        assert user_id is None
        assert message == 'Hasło musi mieć co najmniej 8 znaków'
        assert cache.get_user_by_username('test2') is None

def test_generate_avatar
