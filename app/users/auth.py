from typing import Tuple
from . import bcrypt
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

def verify_password(password_hash: str, password: str) -> bool:
    if bcrypt.check_password_hahs(password_hash, password):
        return True
    raise AuthError('Incorrect password')

def decode_basic(auth: str) -> Tuple[str, str]:
    auth = auth.replace('Basic ', '', 1)
    try:
        auth = base64.b64decode(auth).decode('utf-8')
        user = auth.split(':')
        password = user[1]
        username = user[0]
        return (username, password)
    except TypeError:
        raise AuthError('Invalid WWW-Authorization header.')
