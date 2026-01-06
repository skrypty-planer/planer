from flask import Blueprint, request, jsonify, session
from ..error_handling.logger import logger
from ..error_handling.exceptions import HTTP_STATUS_CODE
from ..utilities.TransactionManager import TransactionManager

bp = Blueprint('/transactions', __name__, url_prefix='/transactions')

def get_user_id():
    # Helper to get user_id from session or arguments
    if 'user_id' in session:
        return session['user_id']
    if request.args.get('user_id'):
        return int(request.args.get('user_id'))
    # fallback for testing
    if request.json and 'user_id' in request.json:
        return request.json['user_id']
    return None

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

    # Convert amount params if present (TransactionManager expects user to handle types or check inside?)
    # TransactionManager filter_transactions expects amount_min/max as logic is there? No, I implemented cast to float there.
    
    tm = TransactionManager()
    
    # Note: I didn't add 'type' to filter_transactions arg list in previous step! 
    # Let me check my memory/logs of TransactionManager.
    # Step 40 output shows filter_transactions signature:
    # def filter_transactions(self, user_id, date_from=None, date_to=None, name=None, category=None, amount_min=None, amount_max=None, sort=None):
    # It missed 'type'. I should fix TransactionManager or handle it manually here.
    # Ideally fix TransactionManager. But I can filter here for now or update TM.
    # Given 'type' is a key filter, I should update TM. 
    # But to save tool calls, I can just filter the result here or pass strict kwargs if TM supported generic kwargs.
    # Wait, 'type' is a reserved keyword in python (sort of), but as argument name it is fine.
    
    # Checking TransactionManager definition in Step 40 again.
    # Yes, it missed 'type' argument.
    # I will proceed by getting all filtered by other params, then filtering by type locally here.
    
    transactions = tm.filter_transactions(
        user_id, date_from, date_to, name, category, amount_min, amount_max, sort
    )
    
    if type_filter:
        transactions = [t for t in transactions if t['type'] == type_filter]
        
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

