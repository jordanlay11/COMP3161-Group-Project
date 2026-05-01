from flask import Blueprint, request, jsonify
from db.db import get_db_connection
from utils.auth import require_auth, require_role

content_api = Blueprint('content_api', __name__)