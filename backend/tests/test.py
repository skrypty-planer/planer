import pytest

def test_if_flask_imports_correctly():
    try:
        import flask
    except ImportError:
        pytest.fail("Flask could not be imported")