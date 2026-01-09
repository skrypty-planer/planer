
import pytest
from flask import Flask
from .conftests import app, client, cache
from ..src.models.user import User
from ..src.utilities.CacheManager import CacheManager

def test_user_management(app: Flask, cache: CacheManager):
    # 1. Test set_user and get_user
    user_data = {
        'user_id': 'u1',
        'username': 'User1',
        'password': 'pwd',
        'transactions': [],
        'funds': 0,
        'avatar_url': ''
    }
    cache.set_user('u1', user_data)
    
    retrieved_user = cache.get_user('u1')
    assert retrieved_user == user_data
    
    # 2. Test get_user_by_username
    found_user = cache.get_user_by_username('User1')
    assert found_user == user_data
    
    found_user_case = cache.get_user_by_username('user1') # Case insensitive check
    assert found_user_case == user_data
    
    # 3. Test get_number_of_users
    assert cache.get_number_of_users() == 1
    
    # Add another user
    user2 = User('u2', 'User2', 'pwd')
    cache.set_user('u2', user2) # Test setting User object
    assert cache.get_number_of_users() == 2
    assert cache.get_user('u2')['username'] == 'User2'

def test_transaction_management(app: Flask, cache: CacheManager):
    # Setup user
    user = User('t_user', 'TransUser', 'pwd')
    cache.set_user('t_user', user)
    
    # 1. Add transaction (Income)
    trans1 = {'id': 't1', 'type': 'income', 'amount': 100}
    cache.add_transaction('t_user', trans1)
    
    user_data = cache.get_user('t_user')
    assert user_data['funds'] == 100
    assert len(user_data['transactions']) == 1
    assert user_data['transactions'][0] == trans1
    
    # 2. Add transaction (Expense)
    trans2 = {'id': 't2', 'type': 'expense', 'amount': 50}
    cache.add_transaction('t_user', trans2)
    
    user_data = cache.get_user('t_user')
    assert user_data['funds'] == 50
    assert len(user_data['transactions']) == 2
    
    # 3. List transactions
    transactions = cache.list_transactions('t_user')
    assert len(transactions) == 2
    assert transactions[1]['id'] == 't2'
    
    # 4. Count transactions
    assert cache.get_number_of_transactions_for_user('t_user') == 2
    
    # 5. Edge case: Add to non-existent user
    res = cache.add_transaction('unknown', trans1)
    assert res is None