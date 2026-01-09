
import pytest
from flask import Flask
from flask.testing import FlaskClient
from .conftests import app, client

def test_health(client: FlaskClient):
    res = client.get('/check/health')
    assert res.status_code == 200
    assert res.get_json()['status_code'] == 200
