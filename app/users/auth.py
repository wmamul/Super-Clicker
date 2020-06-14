from functools import wraps
from datetime import datetime, timedelta
from app import app, db, bcrypt, login_manager
from app.api import parser
import app.database.interface as db_interface
from app.exceptions import DatabaseError, AuthError
from flask import jsonify, request
import jwt

@login_manager.user_loader
def load_user(user_id):
    return db_interface.query_user(int(user_id))

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        try:
            parsed_args = parser.parse_args()
            token = db_interface.query_token(parsed_args['key'])
            if token.is_valid():
                pass
            else:
                raise AuthError('Token expired')
        except:
            return jsonify({'message': 'Invalid or expired token'}), 403

        return f(*args, **kwargs)

    return decorator

def password_is_valid(username, password):
    user = db_interface.query_user(username)    
    if user:
        if bcrypt.check_password_hash(user.password_hash, password):
            return True
        else:
            return False
    else:
        raise DatabaseError('User does not exist: ' + username)
    
def token_is_valid(username):
    user = db_interface.query_user(username)
    if user:
        pass