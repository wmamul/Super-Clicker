from functools import wraps
from datetime import datetime, timedelta
from app import app, db, bcrypt, login_manager
from app.database.models import User, Token
from app.exceptions import DatabaseError, AuthError
from flask import jsonify, request
import jwt

EXP_TIME = 3600 # token expiry time in seconds

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#TODO: Query for token as request argument
def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        try:
            token = Token.query.get(data['token'])
            if token.is_valid():
                pass
            else:
                raise AuthError('Token expired')
        except:
            return jsonify({'message': 'Invalid or expired token'}), 403

        return f(*args, **kwargs)

    return decorator

def password_is_valid(username, password):
    user = User.query.get(username)
    
    if user:
        if bcrypt.check_password_hash(user.password_hash, password):
            return True
        else:
            return False
    else:
        raise DatabaseError('User does not exist: ' + username)

def create_token(username):
    user = User.query.get(username)

    if user:
        token = Token(user.id)
        token_jwt = jwt.encode({'username': username, 'token': str(token.id), 'exp': datetime.utcnow() + timedelta(seconds=EXP_TIME)}, app.config['SECRET_KEY'])
        db.session.add(token)
        db.session.commit()
        return token_jwt
    else:
        raise DatabaseError('User does not exist: ' + username)