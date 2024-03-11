from flask import Blueprint, current_app

bp = Blueprint('api_bp', __name__)

# database check
@bp.route('/')
def index():
    try:
        db = current_app.db
        return "Database connected"
    except:
        raise Exception('Database not initialized')