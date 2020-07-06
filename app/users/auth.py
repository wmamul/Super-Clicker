from functools import wraps
from typing import Tuple
from flask import request
from flask_restx import marshal
from . import bcrypt
from app.api import models
from app.exceptions import AuthError, DatabaseError
from app.database import session_scope, interface as db_interface
import base64

def hash_password(password: str) -> str:
    try:
        hash = bcrypt.generate_password_hash(password).decode('utf-8')
        return hash
    except TypeError:
        raise AuthError('Password must be a utf-8 valid string')

def verify_password(password_hash: str, password: str) -> bool:
    if bcrypt.check_password_hash(password_hash, password):
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
        raise AuthError('Invalid Authorization header.')

def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token_auth = request.args.get('Token')
        with session_scope() as session:
            try:
                token = db_interface.query_token(token_auth, session)
            except DatabaseError:
                return marshal(e, models.message), 401
            if token_auth == token.id and token.is_valid():
                return f()
            else:
                raise AuthError('Token expired.')
    return wrapper
