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

@login_manager.request_loader
def load_user(request):

    # Basic Auth authorization
    auth = request.headers.get('Authorization')
    if auth:
        auth = auth.replace('Basic ', '', 1)
        try:
            auth = base64.b64decode(auth).decode('utf-8')
            user = auth.split(':')
            password = user[1]
            username = user[0]
            with session_scope() as session:
                user = db_interface.query_user(username, session)
                if bcrypt.check_password_hash(user.password_hash, password):
                    return user
                else:
                    raise AuthError('Incorrect user:password combination')
        except TypeError:
           raise AuthError('Incorrect authorization key') 

    # API Token authorization
    auth = request.args.get('Token')
    if auth:
        with session_scope() as session:
            user = db_interface.query_token(auth, session)
            return user

    return None
