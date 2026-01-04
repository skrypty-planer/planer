from flask import Blueprint

bp = Blueprint('/transaction', __name__, url_prefix='/transaction')

@bp.route('/store', methods=['POST'])
def store():
    pass
        

@bp.route('/get', methods=['GET'])
def get():
    pass