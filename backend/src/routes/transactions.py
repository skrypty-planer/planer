from flask import Blueprint, request, jsonify, session, current_app

from backend.src.error_handling.exceptions import DATA_NOT_FOUND_EXCEPTION, INTERNAL_ERROR_EXCEPTION, HTTP_STATUS_CODE
from backend.src.utilities.TransactionManager import TransactionManager
from ..error_handling.logger import logger

bp = Blueprint('/transactions', __name__, url_prefix='/transactions')

@bp.route('/get', methods=["GET"])
def get_transactions():
    trans = TransactionManager()
    
    user_id = request.json['user_id']
    
    if user_id is None:
        user_id = session['user_id']  # get id from session
    try:
        transactions = trans.list_transactions(user_id)
        
        if len(current_app.pending_errors) > 0:
            err = {
                'message': current_app.pending_errors[0].error,
                'status_code': current_app.pending_errors[0].status_code
            }
            current_app.pending_errors = []
            return jsonify(err)
        
        logger.info('Get transactions successful.')
        return jsonify({
            'transactions': transactions,
            'status_code': HTTP_STATUS_CODE.OK
        })
    except DATA_NOT_FOUND_EXCEPTION or INTERNAL_ERROR_EXCEPTION as ex:
        logger.error(ex.error)
        return jsonify({
            'message': 'error',
            'status_code': 400
        })

@bp.route('/filter', methods=["GET"])
def filter_transactions():
    trans = TransactionManager()
    
    user_id = session['user_id']  # get id from session
    filters = {
        "date_from": request.args.get("date_from"),
        "date_to": request.args.get("date_to"),
        "name": request.args.get("name"),
        "category": request.args.get("category"),
        "amount_min": request.args.get("amount_min"),
        "amount_max": request.args.get("amount_max")
    }

    try:
        transactions = trans.filter_transactions(user_id, **filters)
        
        if len(current_app.pending_errors) > 0:
            err = {
                'message': current_app.pending_errors[0].error,
                'status_code': current_app.pending_errors[0].status_code
            }
            current_app.pending_errors = []
            return jsonify(err)
        
        logger.info('Filter transactions successful.')
        return jsonify({
            'transactions': transactions,
            'status_code': HTTP_STATUS_CODE.OK
        })
    except INTERNAL_ERROR_EXCEPTION as ex:
        logger.error(ex.error)
        return jsonify({
            'message': ex.error,
            'status_code': ex.status_code
        })

@bp.route('/store', methods=["POST"])
def add_transaction():
    trans = TransactionManager()
    
    user_id = session['user_id']  # get id from session
    data = request.json

    try:
        transaction = trans.add_transaction(
            user_id=user_id,
            name=data['Nazwa'],
            transaction_type=data['Typ'],
            amount=data['Kwota'],
            category=data["Kategoria"]
        )
        
        if len(current_app.pending_errors) > 0:
            err = {
                'message': current_app.pending_errors[0].error,
                'status_code': current_app.pending_errors[0].status_code
            }
            current_app.pending_errors = []
            return jsonify(err)
        
        logger.info('Transaction added.')
        return jsonify({
            'transaction': transaction,
            'status_code': HTTP_STATUS_CODE.OK
        })
    except DATA_NOT_FOUND_EXCEPTION or INTERNAL_ERROR_EXCEPTION as ex:
        logger.error(ex.error)
        return jsonify({
            'message': "error",
            'status_code': 400
        })

