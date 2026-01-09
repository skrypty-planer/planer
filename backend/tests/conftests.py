import pytest
from flask import Flask
from flask.testing import FlaskClient
from .__init__ import create_app, AuthManager, CacheManager, TransactionManager

@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()

@pytest.fixture
def app():
    # Reset Singletons to ensure fresh state and correct app instance binding
    CacheManager.instance = None
    AuthManager.instance = None
    TransactionManager.instance = None

    app = create_app({
        'TESTING': True,
        'CACHE_TYPE': "SimpleCache",
        'CACHE_DEFAULT_TIMEOUT':3600
    })

    yield app

@pytest.fixture
def auth() -> AuthManager:
    return AuthManager()

@pytest.fixture
def cache() -> CacheManager:
    return CacheManager()

@pytest.fixture
def transaction() -> TransactionManager:
    return TransactionManager()
