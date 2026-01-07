from flask import Blueprint, request, jsonify, session
from ..error_handling.logger import logger
from ..error_handling.exceptions import HTTP_STATUS_CODE
from ..utilities.AuthManager import AuthManager

bp = Blueprint('/auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    avatar_url = data.get('avatarUrl')
    
    if not username or not password:
        return jsonify({'message': 'Brak wymaganych danych', 'status_code': 400})

    auth = AuthManager()
    user_id, error = auth.register_user(username, password, avatar_url)
    
    if error:
        return jsonify({'message': error, 'status_code': 400})

    # Auto login
    session['user_id'] = user_id
    
    logger.info(f'User registered: {user_id}')
    return jsonify({
        'user': {'id': user_id, 'username': username, 'avatarUrl': avatar_url}, # Helper structure
        'status_code': HTTP_STATUS_CODE.OK
    })

@bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'message': 'Brak wymaganych danych', 'status_code': 400})

    auth = AuthManager()
    user_id, error = auth.login(username, password)
    
    if error:
        return jsonify({'message': error, 'status_code': 401})

    session['user_id'] = user_id
    
    logger.info(f'User logged in: {user_id}')
    return jsonify({
        'user_id': user_id,
        'status_code': HTTP_STATUS_CODE.OK
    })

@bp.route('/guest-login', methods=['POST'])
def guest_login():
    auth = AuthManager()
    user_id = auth.login_guest()
    
    session['user_id'] = user_id
    
    logger.info(f'Guest logged in: {user_id}')
    return jsonify({
        'user_id': user_id,
        'status_code': HTTP_STATUS_CODE.OK
    })

@bp.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'status_code': HTTP_STATUS_CODE.OK})

@bp.route('/me', methods=['GET'])
def me():
    
    user_id = session.get('user_id')
    
    from ..utilities.CacheManager import CacheManager
    cache = CacheManager()
    
    if not user_id:
        return jsonify({'message': 'Unauthorized', 'status_code': 401})
        
    user = cache.get_user(user_id)
    if not user:
        return jsonify({'message': 'User not found', 'status_code': 404})
        
    # Return user session info
    user_session = {
        'id': user['user_id'],
        'username': user['username'],
        'avatarUrl': user['avatar_url'],
        'password': user['password'] # Included in frontend simulation session
    }

    return jsonify({
        'user': user_session,
        'status_code': HTTP_STATUS_CODE.OK
    })

@bp.route('/update-profile', methods=['PUT'])
def update_profile():
    if 'user_id' not in session:
        return jsonify({'message': 'Unauthorized', 'status_code': 401})
        
    user_id = session['user_id']
    data = request.json
    
    auth = AuthManager()
    success, error = auth.update_profile(
        user_id, 
        username=data.get('username'),
        password=data.get('password'),
        avatar_url=data.get('avatarUrl')
    )
    
    if not success:
        return jsonify({'message': error, 'status_code': 400})
        
    # Return updated session data
    from ..utilities.CacheManager import CacheManager
    user = CacheManager().get_user(user_id)
    user_session = {
        'id': user['user_id'],
        'username': user['username'],
        'avatarUrl': user['avatar_url'],
        'password': user['password']
    }
    
    return jsonify({
        'user': user_session,
        'status_code': HTTP_STATUS_CODE.OK
    })
