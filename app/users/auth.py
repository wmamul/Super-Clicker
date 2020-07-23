import base64
from datetime import datetime
from functools import wraps
from typing import Tuple, Dict
from flask import request
from . import bcrypt
from app.database import session_scope
from app.database.interface import DAO
import app.exceptions as exc

def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            token = _get_token(request.headers.get('Authorization'))
            if _verify_token(token):
                return f(*args, **kwargs)
            else:
                raise exc.AuthError('Token expired, login again to refresh.')
        except (exc.SessionError, exc.AuthError) as e:
            raise e
    return wrapper

def hash_password(password: str) -> str:
    try:
        hash = bcrypt.generate_password_hash(password).decode('utf-8')
        return hash
    except TypeError:
        raise exc.AuthError('Password must be a utf-8 valid string')

def _verify_password(password_hash: str, password: str) -> bool:
        if bcrypt.check_password_hash(password_hash, password):
            return True
        raise exc.AuthError('Incorrect password')

def _decode_basic(header: str) -> Tuple[str, str]:
    try:
        header = header.replace('Basic ', '', 1)
        header = base64.b64decode(header).decode('utf-8')
        user = header.split(':')
        password = user[1]
        username = user[0]
        return (username, password)
    except (TypeError, AttributeError):
        raise exc.AuthError('Invalid Authorization header.')

def _get_token(auth: str) -> str:
    try:
        return auth.replace('Token ', '', 1)
    except (TypeError,  AttributeError):
        raise exc.AuthError('Invalid Authorization header.')

def _verify_token(token_string: str) -> bool:
    with session_scope() as session:
        try:
            db_interface = DAO(session)
            db_interface.query(token_string)
            token = db_interface.token
            if token['exp'] > datetime.utcnow():
                return True

            else: 
                del db_interface.token
                return False

        except exc.SessionError:
            raise exc.AuthError('Token invalid or expired.')

def login(header: str) -> Dict:
    try:

        if 'Basic' in header:
            username, password = _decode_basic(header)
            with session_scope() as session:
                db_interface = DAO(session)
                db_interface.query(username)
                user_data = db_interface.user
                if _verify_password(user_data['password'], password):
                    db_interface.assign_token()
                    return db_interface.token

        elif 'Token' in header:
            token_str = _get_token(header)
            with session_scope() as session:
                db_interface = DAO(session)
                db_interface.query(token_str)
                db_interface.refresh_token()
                return db_interface.token

        else:
            raise exc.AuthError('Invalid authentication method.')

    except exc.SessionError as e:
        raise exc.AuthError('Authentication failed. ' + str(e)) 

def logout(header: str) -> None:
    try:
 
        token_str = _get_token(header)
        with session_scope() as session:
            db_interface = DAO(session)
            db_interface.query(token_str)
            del db_interface.token

    except (exc.AuthError, exc.SessionError) as e:
        raise e
