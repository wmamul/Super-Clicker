from . import bcrypt, login_manager
from app import app
from app.database import session_scope, interface as db_interface
from app.exceptions import AuthError, DatabaseError
import base64

def hash_password(password: str) -> str:
    try:
        hash = bcrypt.generate_password_hash(password).decode('utf-8')
        return hash
    except TypeError:
        raise AuthError('Password must be a utf-8 valid string')

def check_password(username: str, password: str) -> bool:
    user = interface.query_user(username)
    if bcrypt.check_password_hash(user.password_hash, password):
        return True
    raise AuthError('Invalid password.')

def encode_token(token):
    return jwt.encode({'token_id': token.id, 'user_id': token.user_id},
            app.config['SECRET_KEY']).decode('utf-8')

def decode_token(jwt_string):
    token = jwt.decode(jwt_string, app.config['SECRET_KEY'])
    return token['token_id']

@login_manager.request_loader
def load_user(request):
    auth = request.headers.get('Authorization')
    if auth:
        auth = auth.replace('Basic ', '', 1)
        try:
            auth = base64.b64decode(auth).decode('utf-8')
            user = auth.split(':')
            password = user[1]
            user = interface.query_user(user[0])
            if check_password(user.username, password):
                return user
            else:
                raise AuthError('Incorrect user:password combination')
        except TypeError:
           raise AuthError('Incorrect Authentication key') 
