from ..src.__init__ import create_app

def test_create_app():
    """
        tests create app config, the rest will be tested and checked during other tests
    """
    assert not create_app().testing
    assert create_app(test_config={'TESTING': True}).testing
