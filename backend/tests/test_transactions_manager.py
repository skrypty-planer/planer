import pytest
from datetime import datetime, timedelta

from ..src.utilities.TransactionManager import TransactionManager
from ..src.models.user import User
from ..src.models.transaction import Transaction


# Helpef funcs
def add_test_user(app, user_id=1, funds=1000):
    """
    Adds a test user to CacheManager singleton
    """
    cm = app.cache_manager
    user = User(
        _id=user_id,
        _username=f"user{user_id}",
        _password="password",
        _transactions=[],
        _funds=funds
    )
    cm.set_user(user_id, user.get_obj())
    return user


def add_test_transaction(app, user_id=1, name="Test", amount=100, tx_type="income", category="Pensja", days_ago=0):
    """
    Adds a transaction to a user in CacheManager singleton
    """
    cm = app.cache_manager
    user = cm.get_user(user_id)
    tx = Transaction(
        _id=f"{user_id}-{int(datetime.now().timestamp() * 1000)}",
        _name=name,
        _category=category,
        _amount=amount,
        _transaction_type=tx_type,
        _date=datetime.now().strftime("%Y-%m-%d")
    )
    user['transactions'].append(tx.get_obj())
    cm.set_user(user_id, user)
    return tx


# Ensure user data
def test_ensure_user_data_no_user(app):
    tm = TransactionManager()
    with app.app_context():
        result = tm.ensure_user_data(999)

    assert result is None


def test_ensure_user_data_generates_transactions(app):
    tm = TransactionManager()
    with app.app_context():
        add_test_user(app, user_id=1)
        transactions = tm.ensure_user_data(1)

    assert isinstance(transactions, list)
    assert len(transactions) == 150
    assert "amount" in transactions[0]


# List transactions
def test_list_transactions_returns_data(app):
    tm = TransactionManager()
    with app.app_context():
        add_test_user(app, user_id=1)
        txs = tm.list_transactions(1)

    assert len(txs) == 150


# Dashboard summary
def test_get_dashboard_summary(app):
    tm = TransactionManager()
    with app.app_context():
        add_test_user(app, user_id=1)
        add_test_transaction(app, user_id=1, amount=200, tx_type="income")
        add_test_transaction(app, user_id=1, amount=50, tx_type="expense")

        summary = tm.get_dashboard_summary(1)

    assert "incomeDaily" in summary
    assert "expenseDaily" in summary
    assert "balanceDaily" in summary
    assert summary["balanceDaily"] == summary["incomeDaily"] - summary["expenseDaily"]


# Recent transactions
def test_get_recent_transactions(app):
    tm = TransactionManager()
    with app.app_context():
        add_test_user(app, user_id=1)
        for i in range(10):
            add_test_transaction(app, user_id=1, name=f"Tx {i}")

        recent = tm.get_recent_transactions(1)

    assert len(recent) == 5


# Filter transactions
def test_filter_transactions_by_type_and_amount(app):
    tm = TransactionManager()
    with app.app_context():
        add_test_user(app, user_id=1)
        add_test_transaction(app, 1, amount=500, tx_type="income")
        add_test_transaction(app, 1, amount=50, tx_type="expense")
        add_test_transaction(app, 1, amount=70, tx_type="expense")

        result = tm.filter_transactions(
            user_id=1,
            amount_min=60
        )

    assert all(tx["amount"] >= 60 for tx in result)


def test_filter_transactions_sort_amount_desc(app):
    tm = TransactionManager()
    with app.app_context():
        add_test_user(app, 1)
        add_test_transaction(app, 1, amount=100)
        add_test_transaction(app, 1, amount=300)
        add_test_transaction(app, 1, amount=200)

        result = tm.filter_transactions(1, sort="amount-desc")

    amounts = [t["amount"] for t in result]
    assert amounts == sorted(amounts, reverse=True)


# Get charts
def test_get_charts_structure(app):
    tm = TransactionManager()
    with app.app_context():
        add_test_user(app, user_id=1)
        charts = tm.get_charts(1)

    assert "daily" in charts
    assert "weekly" in charts
    assert "monthly" in charts
    assert "unified" in charts
    assert "averages" in charts
    assert "ranking" in charts


# Get category breakdown
def test_get_category_breakdown_monthly(app):
    tm = TransactionManager()
    with app.app_context():
        add_test_user(app, 1)
        add_test_transaction(app, 1, amount=100, tx_type="expense", category="Food")
        add_test_transaction(app, 1, amount=200, tx_type="expense", category="Food")
        add_test_transaction(app, 1, amount=50, tx_type="expense", category="Transport")

        breakdown = tm.get_category_breakdown(1, "expense", "monthly")

    assert len(breakdown) == 2
    assert breakdown[0]["amount"] >= breakdown[1]["amount"]
    assert breakdown[0]["percentage"] > 0


# Add transactions
def test_add_transaction_updates_funds(app):
    tm = TransactionManager()
    with app.app_context():
        add_test_user(app, 1, funds=1000)

        tx = tm.add_transaction(
            user_id=1,
            name="Bonus",
            transaction_type="income",
            amount=500,
            category="Work"
        )

        user = app.cache_manager.get_user(1)

    assert tx["amount"] == 500
    assert user["funds"] == 1500
    assert user["transactions"][0]["id"] == tx["id"]


# Update transactions
def test_update_transaction_success(app):
    tm = TransactionManager()
    with app.app_context():
        add_test_user(app, 1, funds=1000)
        tx = add_test_transaction(app, 1, amount=100, tx_type="expense")

        updated = tm.update_transaction(
            user_id=1,
            transaction_id=tx.id,
            updates={"amount": 200}
        )

        user = app.cache_manager.get_user(1)

    assert updated["amount"] == 200
    assert user["funds"] == 900  # -100 -> -200 (delta -100)


def test_update_transaction_not_found(app):
    tm = TransactionManager()
    with app.app_context():
        add_test_user(app, 1)
        result = tm.update_transaction(1, "invalid-id", {"amount": 100})

    assert result is None


# Delete transactions
def test_delete_transaction_success(app):
    tm = TransactionManager()
    with app.app_context():
        add_test_user(app, 1, funds=1000)
        tx = add_test_transaction(app, 1, amount=200, tx_type="income")

        success = tm.delete_transaction(1, tx.id)
        user = app.cache_manager.get_user(1)

    assert success is True
    assert user["funds"] == 800
    assert all(t["id"] != tx._id for t in user["transactions"])


def test_delete_transaction_not_found(app):
    tm = TransactionManager()
    with app.app_context():
        add_test_user(app, 1)
        success = tm.delete_transaction(1, "invalid-id")

    assert success is False
