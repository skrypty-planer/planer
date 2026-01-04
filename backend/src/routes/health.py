from flask import Blueprint, request, jsonify, session
from ..error_handling.logger import logger

bp = Blueprint('/check', __name__, url_prefix='/check')

@bp.route('/health', methods=['GET'])
def health():
    try:
        return jsonify({
            'status_code': 200
        })
    except Exception as ex:
        return jsonify({
            'status_code': 400,
            'exception': ex
        })
