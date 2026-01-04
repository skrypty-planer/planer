from flask import Blueprint, request, jsonify, session
from ..error_handling.logger import logger
from ..error_handling.exceptions import DATA_NOT_FOUND_EXCEPTION, INTERNAL_ERROR_EXCEPTION, UNAUTHORIZED_EXCEPTION, HTTP_STATUS_CODE
from ..utilities.global_utils import check_if_data_is_not_None
from ..utilities.AuthManager import AuthManager
from ..utilities.CacheManager import CacheManager

bp = Blueprint('/auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['POST'])
def login():
    try:
        username = request.json['username']
        password = request.json['password']
    except Exception as ex:
        return jsonify({
            'message': 'keyerror',
            'status_code': 400
        })
    
    auth = AuthManager()
    
    try:
        auth.check_if_user_is_logged_in(username)
        user_id = auth.create_user(username, password)

        session['user_id'] = user_id  # save current user's user_id to session for further use

        logger.info('User logged in.')
        return jsonify({
            'user_id': user_id,
            'status_code': HTTP_STATUS_CODE.OK
        })
    except INTERNAL_ERROR_EXCEPTION as ex:
        return jsonify({
            'message': INTERNAL_ERROR_EXCEPTION.error,
            'status_code': INTERNAL_ERROR_EXCEPTION.status_code
        })
        

@bp.route('/me', methods=['GET'])
def me():
    try:
        user_id = request.json['user_id']
    except Exception as ex:
        return jsonify({
            'message': 'keyerror',
            'status_code': 400
        })
    
    auth = AuthManager()
    cache = CacheManager()
    
    try:
        check_if_data_is_not_None([user_id])
        user = cache.get_user(user_id)
        auth.check_if_user_is_logged_in(user.username)
        return jsonify({
            'user_id': user_id,
            'user': user,
            'status_code': HTTP_STATUS_CODE.OK
        })
    except UNAUTHORIZED_EXCEPTION as ex:
        return jsonify({
            'message': UNAUTHORIZED_EXCEPTION.error,
            'status_code': UNAUTHORIZED_EXCEPTION.status_code
        })
