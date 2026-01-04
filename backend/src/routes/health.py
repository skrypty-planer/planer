from flask import Blueprint, request, jsonify

bp = Blueprint('/auth', __name__, url_prefix='/auth')

@bp.route("/health")
def health():
    return jsonify({"status": "ok"}), 200