import pytest
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


# Recent transactions
def test_get_recent_unauthorized(client):
    response = client.get(
        '/transactions/recent',
        json={}
    )
    data = response.get_json()

    assert response.status_code == 401
    assert data['message'] == 'Unauthorized'


def test_get_recent_success(client, app):
    with app.app_context():
        add_test_user(app, user_id=1)
        add_test_transaction(app, user_id=1, name="Tx 1")
        add_test_transaction(app, user_id=1, name="Tx 2")

    with client.session_transaction() as sess:
        sess['user_id'] = 1

    response = client.get('/transactions/recent')
    data = response.get_json()

    assert response.status_code == 200
    assert 'transactions' in data
    assert isinstance(data['transactions'], list)
    assert len(data['transactions']) >= 2


# Get transactions
def test_get_transactions_unauthorized(client):
    response = client.get(
        '/transactions/get',
        json={}
    )
    data = response.get_json()

    assert response.status_code == 401
    assert data['message'] == 'Unauthorized'


def test_get_transactions_success(client, app):
    with app.app_context():
        add_test_user(app, user_id=1)
        add_test_transaction(app, user_id=1, name="Salary", tx_type="income")
        add_test_transaction(app, user_id=1, name="Groceries", tx_type="expense")

    with client.session_transaction() as sess:
        sess['user_id'] = 1

    response = client.get(
        '/transactions/get',
        query_string={'type': 'expense'}
    )
    data = response.get_json()

    assert response.status_code == 200
    assert 'items' in data
    assert 'meta' in data
    assert isinstance(data['items'], list)
    assert data['meta']['total'] == len(data['items'])

    for tx in data['items']:
        assert tx['type'] == 'expense'


# Get charts
def test_get_charts_unauthorized(client):
    response = client.get(
        '/transactions/charts',
        json={}
    )
    data = response.get_json()

    assert response.status_code == 401
    assert data['message'] == 'Unauthorized'


def test_get_charts_success(client, app):
    with app.app_context():
        add_test_user(app, user_id=1)
        add_test_transaction(app, user_id=1)

    with client.session_transaction() as sess:
        sess['user_id'] = 1

    response = client.get('/transactions/charts')
    data = response.get_json()

    assert response.status_code == 200
    assert 'charts' in data


# Categories breakdown
def test_get_categories_unauthorized(client):
    response = client.get(
        '/transactions/categories',
        json={}
    )
    data = response.get_json()

    assert response.status_code == 401
    assert data['message'] == 'Unauthorized'


def test_get_categories_default_success(client, app):
    with app.app_context():
        add_test_user(app, user_id=1)
        add_test_transaction(app, user_id=1, category="Food")

    with client.session_transaction() as sess:
        sess['user_id'] = 1

    response = client.get('/transactions/categories')
    data = response.get_json()

    assert response.status_code == 200
    assert 'breakdown' in data


def test_get_categories_with_params(client, app):
    with app.app_context():
        add_test_user(app, user_id=1)
        add_test_transaction(app, user_id=1, tx_type="income", category="Salary")

    with client.session_transaction() as sess:
        sess['user_id'] = 1

    response = client.get(
        '/transactions/categories',
        query_string={'type': 'income', 'period': 'yearly'}
    )
    data = response.get_json()

    assert response.status_code == 200
    assert 'breakdown' in data


# Store transaction
def test_add_transaction_unauthorized(client):
    response = client.post(
        '/transactions/store',
        json={}
    )
    data = response.get_json()

    assert response.status_code == 401
    assert data['message'] == 'Unauthorized'


def test_add_transaction_success(client, app):
    with app.app_context():
        add_test_user(app, user_id=1)

    with client.session_transaction() as sess:
        sess['user_id'] = 1

    response = client.post(
        '/transactions/store',
        json={
            'name': 'Bonus',
            'amount': 500,
            'type': 'income',
            'category': 'Work'
        }
    )
    data = response.get_json()

    assert response.status_code == 200
    assert 'transaction' in data


# Update transaction
def test_update_transaction_not_found(client, app):
    with app.app_context():
        add_test_user(app, user_id=1)

    with client.session_transaction() as sess:
        sess['user_id'] = 1

    response = client.put(
        '/transactions/update/invalid-id',
        json={'amount': 999}
    )
    data = response.get_json()

    assert response.status_code == 404
    assert data['message'] == 'Not found'


def test_update_transaction_success(client, app):
    with app.app_context():
        add_test_user(app, user_id=1)
        tx = add_test_transaction(app, user_id=1, amount=100)

    with client.session_transaction() as sess:
        sess['user_id'] = 1

    response = client.put(
        f'/transactions/update/{tx.id}',
        json={'amount': 200}
    )
    data = response.get_json()

    assert response.status_code == 200
    assert data['transaction']['amount'] == 200


# Delete transaction
def test_delete_transaction_not_found(client, app):
    with app.app_context():
        add_test_user(app, user_id=1)

    with client.session_transaction() as sess:
        sess['user_id'] = 1

    response = client.delete('/transactions/delete/invalid-id')
    data = response.get_json()

    assert response.status_code == 404
    assert data['message'] == 'Not found or failed'


def test_delete_transaction_success(client, app):
    with app.app_context():
        add_test_user(app, user_id=1)
        tx = add_test_transaction(app, user_id=1)

    with client.session_transaction() as sess:
        sess['user_id'] = 1

    response = client.delete(
        f'/transactions/delete/{tx.id}'
    )
    data = response.get_json()

    assert response.status_code == 200
    assert data['success'] is True
