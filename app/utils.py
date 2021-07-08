# Internal imports
from app.customer.models import Users
from app.config import Config

# External imports
from flask import request, jsonify
from functools import wraps
import jwt

def get_key(val, dict):
    for key, value in dict.items():
        if val == value:
            return key


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'Message': 'Missing token'}), 401
        try:
            data = jwt.decode(
                token, Config.SECRET_KEY, algorithms=['HS256'])
            current_user = Users.query.filter_by(
                pub_id=data['pub_id']).first()
        except Exception as ex:
            return jsonify({'Message': 'Invalid token'}), 401
        return f(current_user, *args, **kwargs)
    return decorated
