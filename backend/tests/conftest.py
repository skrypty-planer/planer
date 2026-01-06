import pytest

from flask_caching import Cache
from ..src.utilities.CacheManager import CacheManager
from ..src.utilities.TransactionManager import TransactionManager
from ..src.app import create_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def app():
    CacheManager.instance = None

    app = create_app({
        'TESTING': True,
        "CACHE_TYPE": "SimpleCache",
        "CACHE_DEFAULT_TIMEOUT": 60,
    })

    yield app