from flask import Blueprint, request, jsonify
from ..utilities.global_utils import get_user_id
from ..error_handling.logger import logger
from ..error_handling.exceptions import HTTP_STATUS_CODE
from ..utilities.TransactionManager import TransactionManager

bp = Blueprint('/transactions', __name__, url_prefix='/transactions')

@bp.route('/summary', methods=['GET'])
def get_summary():
    user_id = get_user_id()
    if not user_id: return jsonify({'message': 'Unauthorized'}), 401
    
    tm = TransactionManager()
    summary = tm.get_dashboard_summary(user_id)
    return jsonify({'summary': summary}), 200

@bp.route('/recent', methods=['GET'])
def get_recent():
    user_id = get_user_id()
    if not user_id: return jsonify({'message': 'Unauthorized'}), 401
    
    tm = TransactionManager()
    transactions = tm.get_recent_transactions(user_id)
    return jsonify({'transactions': transactions}), 200

@bp.route('/get', methods=['GET'])
def get_transactions():
    user_id = get_user_id()
    if not user_id: return jsonify({'message': 'Unauthorized'}), 401
    
    # Filters
    date_from = request.args.get('dateFrom')
    date_to = request.args.get('dateTo')
    name = request.args.get('name')
    category = request.args.get('category')
    amount_min = request.args.get('amountMin')
    amount_max = request.args.get('amountMax')
    type_filter = request.args.get('type')
    sort = request.args.get('sort')
    
    tm = TransactionManager()
    
    transactions = tm.filter_transactions(
        user_id, date_from, date_to, name, category, amount_min, amount_max, sort, type_filter
    )
        
    return jsonify({
        'items': transactions,
        'meta': {'total': len(transactions)}
    }), 200

@bp.route('/charts', methods=['GET'])
def get_charts():
    user_id = get_user_id()
    if not user_id: return jsonify({'message': 'Unauthorized'}), 401
    
    tm = TransactionManager()
    charts = tm.get_charts(user_id)
    return jsonify({'charts': charts}), 200

@bp.route('/categories', methods=['GET'])
def get_categories_breakdown():
    user_id = get_user_id()
    if not user_id: return jsonify({'message': 'Unauthorized'}), 401
    
    type_filter = request.args.get('type', 'expense')
    period = request.args.get('period', 'monthly')
    
    tm = TransactionManager()
    breakdown = tm.get_category_breakdown(user_id, type_filter, period)
    return jsonify({'breakdown': breakdown}), 200

@bp.route('/store', methods=['POST'])
def add_transaction():
    user_id = get_user_id()
    if not user_id: return jsonify({'message': 'Unauthorized'}), 401
    
    data = request.json
    # Frontend sends: { name, amount, date, type, category }
    # TransactionManager.add_transaction(user_id, name, transaction_type, amount, category)
    
    tm = TransactionManager()
    try:
        tx = tm.add_transaction(
            user_id,
            name=data['name'],
            transaction_type=data['type'],
            amount=data['amount'],
            category=data['category']
        )
        return jsonify({'transaction': tx, 'status_code': HTTP_STATUS_CODE.OK})
    except Exception as e:
        logger.error(str(e))
        return jsonify({'message': str(e)}), 400

@bp.route('/update/<transaction_id>', methods=['PUT'])
def update_transaction(transaction_id):
    user_id = get_user_id()
    if not user_id: return jsonify({'message': 'Unauthorized'}), 401
    
    updates = request.json
    tm = TransactionManager()
    tx = tm.update_transaction(user_id, transaction_id, updates)
    
    if tx:
        return jsonify({'transaction': tx}), 200
    return jsonify({'message': 'Not found'}), 404

@bp.route('/delete/<transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    user_id = get_user_id()
    if not user_id: return jsonify({'message': 'Unauthorized'}), 401
    
    tm = TransactionManager()
    success = tm.delete_transaction(user_id, transaction_id)
    
    if success:
        return jsonify({'success': True}), 200
    return jsonify({'message': 'Not found or failed'}), 404

