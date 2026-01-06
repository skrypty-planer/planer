import pytest
from ..src.utilities.CacheManager import CacheManager
from ..src.utilities.TransactionManager import TransactionManager
from ..src.models.user import User
from ..src.models.transaction import Transaction
from datetime import datetime

# Helper functions
def add_test_user(app, user_id=1):
    """
    Adds a test user to CacheManager singleton
    """
    cm = app.cache_manager
    user = User(
        _id=user_id,
        _username=f"user{user_id}",
        _password="password",
        _transactions=[],
        _funds=1000
    )
    cm.set_user(user_id, user.get_obj())
    return user

def add_test_transaction(app, user_id=1, name="Test Income", amount=100, tx_type="income", category="Pensja"):
    """
    Adds a transaction to a user in CacheManager singleton
    """
    cm = app.cache_manager
    user = cm.get_user(user_id)
    tx = Transaction(
        _id=f"{user_id}-{int(datetime.now().timestamp()*1000)}",
        _name=name,
        _category=category,
        _amount=amount,
        _transaction_type=tx_type,
        _date=datetime.now().strftime("%Y-%m-%d")
    )
    user['transactions'].append(tx.get_obj())
    cm.set_user(user_id, user)
    return tx


# Summary tests
def test_get_summary_unauthorized(client):
    response = client.get(
        '/transactions/summary',
        json={}
    )
    data = response.get_json()

    assert response.status_code == 401
    assert data['message'] == 'Unauthorized'


def test_get_summary_success(client, app):
    # Add user and a transaction
    with app.app_context():
        add_test_user(app, user_id=1)
        add_test_transaction(app, user_id=1)

    # Set user_id in session
    with client.session_transaction() as sess:
        sess['user_id'] = 1

    # Make request
    response = client.get(
        '/transactions/summary',
        query_string={"user_id": 1}
    )
    data = response.get_json()

    assert response.status_code == 200
    assert 'summary' in data