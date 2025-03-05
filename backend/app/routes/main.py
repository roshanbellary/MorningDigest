from flask import Blueprint, jsonify

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return jsonify({"status": "ok", "message": "Morning Digest API is running"})
