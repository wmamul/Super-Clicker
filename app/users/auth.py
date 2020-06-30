from app import app
from app.database import interface
from app.exceptions import AuthError, DatabaseError
import jwt

def encode_token(token):
    return jwt.encode({'token_id': token.id, 'user_id': token.user_id}, app.config['SECRET_KEY']).decode('utf-8')

def decode_token(jwt_string):
    token = jwt.decode(jwt_string, app.config['SECRET_KEY'])
    return token['token_id']