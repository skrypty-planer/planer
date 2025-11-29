from flask import Blueprint, request, jsonify
from ..error_handling.logger import logger
from ..error_handling.exceptions import DATA_NOT_FOUND_EXCEPTION, INTERNAL_ERROR_EXCEPTION, UNAUTHORIZED_EXCEPTION, HTTP_STATUS_CODE
from ..utilities.global_utils import check_if_data_is_not_None
from ..utilities.auth_utils import check_if_user_is_logged_in, create_user
from ..utilities.caching_utils import get_user_by_id

bp = Blueprint('/auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']
    
    try:
        check_if_data_is_not_None([username, password])
        check_if_user_is_logged_in(username)
        user_id = create_user(username, password)
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
    
    try:
        check_if_data_is_not_None([user_id])
        user = get_user_by_id(user_id)
        check_if_user_is_logged_in(user.username)
        return jsonify({
            'user_id': user_id,
            'status_code': HTTP_STATUS_CODE.OK
        })
    except DATA_NOT_FOUND_EXCEPTION or UNAUTHORIZED_EXCEPTION as ex:
        logger.error(ex.error)
        return jsonify({
            'message': ex.error,
            'status_code': ex.status_code
        })