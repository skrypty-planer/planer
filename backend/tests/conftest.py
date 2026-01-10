import pytest

from ..src.app import create_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        "CACHE_TYPE": "SimpleCache",
        "CACHE_DEFAULT_TIMEOUT": 60,
    })

    with app.app_context():
        yield app


@pytest.fixture(autouse=True)
def reset_singletons():
    from backend.src.utilities.CacheManager import CacheManager
    from backend.src.utilities.TransactionManager import TransactionManager
    from backend.src.utilities.AuthManager import AuthManager

    CacheManager._instances = {}
    TransactionManager._instances = {}
    AuthManager._instances = {}
    yield
    CacheManager._instances = {}
    TransactionManager._instances = {}
    AuthManager._instances = {}