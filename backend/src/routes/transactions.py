from flask import Blueprint, request, jsonify

from backend.src.error_handling.exceptions import DATA_NOT_FOUND_EXCEPTION, INTERNAL_ERROR_EXCEPTION, HTTP_STATUS_CODE
from backend.src.services.transactions_service import TransactionsService as TxSvc
from ..error_handling.logger import logger

bp = Blueprint('/transactions', __name__, url_prefix='/transactions')

@bp.route('/get', methods=["GET"])
def get_transactions():
    user_id = None  # TODO
    try:
        transactions = TxSvc.list_transactions(user_id)
        logger.info('Get transactions successful.')
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
    user_id = None  # TODO
    data = request.json

    try:
        transaction = TxSvc.add_transaction(
            user_id=user_id,
            category=data["category"],
            amount=data["amount"],
            description="description"
        )
        logger.info('Transaction added.')
        return jsonify({
            'transaction': transaction,
            'status_code': HTTP_STATUS_CODE.OK
        })
    except DATA_NOT_FOUND_EXCEPTION or INTERNAL_ERROR_EXCEPTION as ex:
        logger.error(ex.error)
        return jsonify({
            'message': ex.error,
            'status_code': ex.status_code
        })

