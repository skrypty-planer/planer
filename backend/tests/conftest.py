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
    app = create_app({
        'TESTING': True
    })

    CacheManager(Cache(app))
    TransactionManager()

    yield app