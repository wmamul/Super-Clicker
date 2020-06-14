from . import bcrypt
from app import app
from app.database.interface import query_user
from app.exceptions import AuthError
import jwt

@login_manager.user_loader
def load_user(user_id):
    return query_user(user_id)

def encode_token(token):
    return jwt.encode({'token_id': token.id, 'user_id': token.user_id}, app.config['SECRET_KEY']).decode('utf-8')

def decode_token(jwt_string):
    token = jwt.decode(jwt_string, app.config['SECRET_KEY'])
    return token['token_id']

def check_password(user, password):
    if bcrypt.check_password_hash(user.password_hash, password):
        return True
    raise AuthError('Invalid password.')