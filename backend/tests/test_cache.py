# from .__init__ import client, app
# import pytest

# def test_get(client, app):
#     response = client.post(
#         '/transactions/get', json={'username': 'test', 'password': 'test123'}
#     )
#     assert response.status_code == 200

#     transactions = TxSvc.list_transactions(response.user_id)
#     assert len(transactions) == 1
    


# @pytest.mark.parametrize(('username', 'password', 'status_code'), (
#     ('', '', 400),
#     ('a', '', 400),
#     ('test', 'test123', 200),
# ))
# def test_get_validate_input(client, username, password, status_code):
#     response = client.post(
#         '/transactions/get',
#         json={'username': username, 'password': password}
#     )
#     assert status_code == response.status_code
    
#     transactions = TxSvc.list_transactions(response.user_id)
#     assert len(transactions) == 1

# def test_filter(client, app):
#     response = client.get(
#         '/transactions/filter',
#         json={'user_id': 1}
#     )
#     assert response.status_code == 200
    
#     transactions = TxSvc.list_transactions(response.user_id)
#     assert len(transactions) == 1

# @pytest.mark.parametrize(('user_id', 'status_code'), (
#     ('', 400),
#     ('a', 400),
#     (1, 200),
# ))
# def test_filter_validate_input(client, user_id, status_code):
#     response = client.get(
#         '/transactions/filter',
#         json={'user_id': user_id}
#     )
#     assert status_code == response.status_code
    
#     transactions = TxSvc.list_transactions(response.user_id)
#     assert len(transactions) == 1

# def test_store(client, app):
#     response = client.get(
#         '/transactions/store',
#         json={'user_id': 1}
#     )
#     assert response.status_code == 200
    
#     # with app.app_context():
#     #     assert get_db().execute(
#     #         "SELECT * FROM user WHERE user_id = 1",
#     #     ).fetchone() is not None

# @pytest.mark.parametrize(('user_id', 'status_code'), (
#     ('', 400),
#     ('a', 400),
#     (1, 200),
# ))
# def test_store_validate_input(client, user_id, status_code):
#     response = client.get(
#         '/transactions/store',
#         json={'user_id': user_id}
#     )
#     assert status_code == response.status_code


# @bp.route('/get', methods=["GET"])
# def get_transactions():
#     user_id = session['user_id']  # get id from session
#     try:
#         transactions = TxSvc.list_transactions(user_id)
#         logger.info('Get transactions successful.')
#         return jsonify({
#             'transactions': transactions,
#             'status_code': HTTP_STATUS_CODE.OK
#         })
#     except INTERNAL_ERROR_EXCEPTION as ex:
#         logger.error(ex.error)
#         return jsonify({
#             'message': ex.error,
#             'status_code': ex.status_code
#         })

# @bp.route('/filter', methods=["GET"])
# def filter_transactions():
#     user_id = session['user_id']  # get id from session
#     filters = {
#         "date_from": request.args.get("date_from"),
#         "date_to": request.args.get("date_to"),
#         "name": request.args.get("name"),
#         "category": request.args.get("category"),
#         "amount_min": request.args.get("amount_min"),
#         "amount_max": request.args.get("amount_max")
#     }

#     try:
#         transactions = TxSvc.filter_transactions(user_id, **filters)
#         logger.info('Filter transactions successful.')
#         return jsonify({
#             'transactions': transactions,
#             'status_code': HTTP_STATUS_CODE.OK
#         })
#     except INTERNAL_ERROR_EXCEPTION as ex:
#         logger.error(ex.error)
#         return jsonify({
#             'message': ex.error,
#             'status_code': ex.status_code
#         })

# @bp.route('/store', methods=["POST"])
# def add_transaction():
#     user_id = session['user_id']  # get id from session
#     data = request.json

#     try:
#         transaction = TxSvc.add_transaction(
#             user_id=user_id,
#             name=data['Nazwa'],
#             transaction_type=data['Typ'],
#             amount=data['Kwota'],
#             category=data["Kategoria"]
#         )
#         logger.info('Transaction added.')
#         return jsonify({
#             'transaction': transaction,
#             'status_code': HTTP_STATUS_CODE.OK
#         })
#     except DATA_NOT_FOUND_EXCEPTION or INTERNAL_ERROR_EXCEPTION as ex:
#         logger.error(ex.error)
#         return jsonify({
#             'message': ex.error,
#             'status_code': ex.status_code
#         })

