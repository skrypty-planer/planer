
import pytest
from flask import Flask
from flask.testing import FlaskClient
from .conftests import app, client, auth, cache
from ..src.utilities.AuthManager import AuthManager
from ..src.utilities.CacheManager import CacheManager

def test_register(client: FlaskClient, cache: CacheManager):
    # 1. Valid registration
    res = client.post('/auth/register', json={
        'username': 'test_user',
        'password': 'Password1!',
        'avatarUrl': 'http://avatar.com/1.png'
    })
    assert res.get_json()['status_code'] == 200
    data = res.get_json()
    assert data['user']['username'] == 'test_user'
    assert data['user']['id'] is not None
    
    # Check cache
    user = cache.get_user(data['user']['id'])
    assert user is not None
    assert user['username'] == 'test_user'

    # 2. Missing fields
    res = client.post('/auth/register', json={
        'username': 'test_user2'
    })
    assert res.get_json()['status_code'] == 400
    assert res.get_json()['message'] == 'Brak wymaganych danych'

    # 3. Duplicate username
    res = client.post('/auth/register', json={
        'username': 'test_user', # Already registered
        'password': 'Password1!'
    })
    assert res.get_json()['status_code'] == 400
    assert res.get_json()['message'] == 'Użytkownik o tej nazwie już istnieje'

    # 4. Invalid password
    res = client.post('/auth/register', json={
        'username': 'test_user3',
        'password': 'weak'
    })
    assert res.get_json()['status_code'] == 400
    assert res.get_json()['message'] == 'Hasło musi mieć co najmniej 8 znaków'

def test_login(client: FlaskClient, auth: AuthManager):
    # Setup user
    client.post('/auth/register', json={'username': 'login_user', 'password': 'Password1!'})
    
    # 1. Valid login
    res = client.post('/auth/login', json={
        'username': 'login_user',
        'password': 'Password1!'
    })
    assert res.get_json()['status_code'] == 200
    assert res.get_json()['user_id'] is not None
        
    # 2. Invalid password
    res = client.post('/auth/login', json={
        'username': 'login_user',
        'password': 'WrongPassword'
    })
    assert res.get_json()['status_code'] == 401
    assert res.get_json()['message'] == 'Nieprawidłowa nazwa użytkownika lub hasło'
    
    # 3. Non-existent user
    res = client.post('/auth/login', json={
        'username': 'unknown',
        'password': 'Password1!'
    })
    assert res.get_json()['status_code'] == 401
    
    # 4. Missing fields
    res = client.post('/auth/login', json={
        'username': 'login_user'
    })
    assert res.get_json()['status_code'] == 400

def test_guest_login(client: FlaskClient):
    res = client.post('/auth/guest-login')
    assert res.get_json()['status_code'] == 200
    data = res.get_json()
    assert data['user_id'] == 'guest-user'

def test_logout(client: FlaskClient):
    # Login first
    client.post('/auth/guest-login')
    
    # Logout
    res = client.post('/auth/logout')
    assert res.get_json()['status_code'] == 200
    
    # Verify by checking /me
    res = client.get('/auth/me')
    assert res.get_json()['status_code'] == 401

def test_me(client: FlaskClient):
    # 1. Unauthenticated
    client.post('/auth/logout') # Ensure logged out
    res = client.get('/auth/me')
    assert res.get_json()['status_code'] == 401
    
    # 2. Authenticated
    client.post('/auth/register', json={'username': 'me_user', 'password': 'Password1!'})
    res = client.get('/auth/me')
    assert res.get_json()['status_code'] == 200
    data = res.get_json()
    assert data['user']['username'] == 'me_user'

def test_update_profile(client: FlaskClient):
    # 1. Unauthenticated
    client.post('/auth/logout')
    assert client.get('/auth/me').get_json()['status_code'] == 401
    res = client.put('/auth/update-profile', json={'username': 'new_name'})
    assert res.get_json()['status_code'] == 401
    
    # 2. Authenticated update
    client.post('/auth/register', json={'username': 'update_user', 'password': 'Password1!'})
    
    res = client.put('/auth/update-profile', json={
        'username': 'updated_name',
        'avatarUrl': 'http://new.avatar'
    })
    assert res.get_json()['status_code'] == 200
    data = res.get_json()
    assert data['user']['username'] == 'updated_name'
    assert data['user']['avatarUrl'] == 'http://new.avatar'
    
    # 3. Validation error (password)
    res = client.put('/auth/update-profile', json={
        'password': 'fail'
    })
    assert res.get_json()['status_code'] == 400
    assert 'Hasło' in res.get_json()['message']
