# import pytest
# from flask import g, session, jsonify
# from ..src.error_handling.logger import logger
# from .__init__ import client, app
# from ..src.utilities.TransactionManager import TransactionManager

# def test_login(client, app):
#     trans = TransactionManager()
    
#     response = client.post(
#         '/auth/login', json={'username': 'test', 'password': 'test123'}
#     )
#     assert response.status_code == 200

#     transactions = trans.list_transactions(response.user_id)
#     assert len(transactions) == 1


# @pytest.mark.parametrize(('username', 'password', 'status_code'), (
#     ('', '', 400),
#     ('a', '', 400),
#     ('test', 'test123', 200),
# ))
# def test_login_validate_input(client, username, password, status_code):
#     trans = TransactionManager()
    
#     response = client.post(
#         '/auth/login',
#         json={'username': username, 'password': password}
#     )
#     assert status_code == response.status_code
    
#     transactions = trans.list_transactions(response.user_id)
#     assert len(transactions) == 1


# def test_me(client, app):
#     trans = TransactionManager()
    
#     response = client.get(
#         '/auth/me',
#         json={'user_id': 1}
#     )
#     assert response.status_code == 200
    
#     transactions = trans.list_transactions(response.user_id)
#     assert len(transactions) == 1

# @pytest.mark.parametrize(('user_id', 'status_code'), (
#     ('', 400),
#     ('a', 400),
#     (1, 200),
# ))
# def test_me_validate_input(client, user_id, status_code):
#     trans = TransactionManager()
    
#     response = client.get(
#         '/auth/me',
#         json={'user_id': user_id}
#     )
#     assert status_code == response.status_code
    
#     transactions = trans.list_transactions(response.user_id)
#     assert len(transactions) == 1
