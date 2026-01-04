from flask import Blueprint, request, jsonify, session, current_app
from ..error_handling.logger import logger
from ..error_handling.exceptions import DATA_NOT_FOUND_EXCEPTION, INTERNAL_ERROR_EXCEPTION, UNAUTHORIZED_EXCEPTION, HTTP_STATUS_CODE
from ..utilities.global_utils import check_if_data_is_not_None
from ..utilities.AuthManager import AuthManager
from ..utilities.CacheManager import CacheManager

bp = Blueprint('/auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']
    
    auth = AuthManager()
    
    try:
        check_if_data_is_not_None([username, password])
        auth.check_if_user_is_logged_in(username)
        user_id = auth.create_user(username, password)

        session['user_id'] = user_id  # save current user's user_id to session for further use

        if len(current_app.pending_errors) > 0:
            err = {
                'message': current_app.pending_errors[0].error,
                'status_code': current_app.pending_errors[0].status_code
            }
            current_app.pending_errors = []
            return jsonify(err)

        logger.info('User logged in.')
        return jsonify({
            'user_id': user_id,
            'status_code': HTTP_STATUS_CODE.OK
        })
    except DATA_NOT_FOUND_EXCEPTION or INTERNAL_ERROR_EXCEPTION as ex:
        logger.error(ex.error)
        return jsonify({
            'message': ex.error,
            'status_code': ex.status_code
        })
        

@bp.route('/me', methods=['GET'])
def me():
    user_id = request.json['user_id']
    
    auth = AuthManager()
    cache = CacheManager()
    
    try:
        check_if_data_is_not_None([user_id])
        user = cache.get_user(user_id)
        auth.check_if_user_is_logged_in(user.username)
        
        if len(current_app.pending_errors) > 0:
            err = {
                'message': current_app.pending_errors[0].error,
                'status_code': current_app.pending_errors[0].status_code
            }
            current_app.pending_errors = []
            return jsonify(err)
        
        return jsonify({
            'user_id': user_id,
            'user': user,
            'status_code': HTTP_STATUS_CODE.OK
        })
    except DATA_NOT_FOUND_EXCEPTION or UNAUTHORIZED_EXCEPTION as ex:
        return jsonify({
            'message': ex.error,
            'status_code': ex.status_code
        })
