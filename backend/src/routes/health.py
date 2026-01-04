from flask import Blueprint, request, jsonify

bp = Blueprint()

@bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200