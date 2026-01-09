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


@pytest.mark.parametrize("password, expected_valid, expected_message", [
    ('zaq1@WSX', True, None),
    ('z', False, 'Hasło musi mieć co najmniej 8 znaków'),
    ('zaq1@wsx', False, 'Hasło musi zawierać co najmniej jedną dużą literę'),
    ('zaq@WSXz', False, 'Hasło musi zawierać co najmniej jedną cyfrę'),
    ('zaq1WSXz', False, 'Hasło musi zawierać co najmniej jeden znak specjalny'),
])
def test_validate_password(auth: AuthManager, password, expected_valid, expected_message):
    status, message = auth.validate_password(password)
    assert status == expected_valid
    assert message == expected_message


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



def test_login_guest(auth: AuthManager, cache: CacheManager):
    guest_id = auth.login_guest()
    assert guest_id == 'guest-user'
    
    user = cache.get_user(guest_id)
    assert user is not None
    assert user['username'] == 'Gość'
    
    guest_id_2 = auth.login_guest()
    assert guest_id_2 == guest_id
    user_2 = cache.get_user(guest_id)
    assert user_2 == user

def test_update_profile(app: Flask, client: FlaskClient, auth: AuthManager, cache: CacheManager):
    with client:
        user_id, _ = auth.register_user('update_test', 'zaq1@WSX')
        assert user_id is not None

        success, message = auth.update_profile(user_id, username='test')
        assert success is True
        assert message is None
        user = cache.get_user(user_id)
        assert user['username'] == 'test'
        
        auth.register_user('conflict_user', 'zaq1@WSX')
        success, message = auth.update_profile(user_id, username='conflict_user')
        assert success is False
        assert message == 'Nazwa użytkownika jest już zajęta'
        
        success, message = auth.update_profile(user_id, password='newPassword1!')
        assert success is True
        user = cache.get_user(user_id)
        assert user['password'] == 'newPassword1!'
        
        success, message = auth.update_profile(user_id, password='weak')
        assert success is False
        assert message == 'Hasło musi mieć co najmniej 8 znaków' # First check
        
        new_avatar = 'http://example.com/avatar.png'
        success, message = auth.update_profile(user_id, avatar_url=new_avatar)
        assert success is True
        user = cache.get_user(user_id)
        assert user['avatar_url'] == new_avatar
        
        success, message = auth.update_profile('non-existent', username='ghost')
        assert success is False
        assert message == 'Użytkownik nie znaleziony'
