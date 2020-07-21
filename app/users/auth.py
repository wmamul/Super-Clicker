import base64
from functools import wraps
from typing import Tuple, Dict
from flask import request
from flask_restx import marshal
from . import bcrypt
from app.api import models
import app.exceptions as exc
from app.database import session_scope
from app.database.interface import DAO

def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            token = _get_token(request.headers.get('Authorization'))
            if _validate_token(token):
                return f(*args, **kwargs)
            else:
                raise exc.AuthError('Token expired, login again to refresh.')
        except (exc.SessionError, exc.AuthError) as e:
            return marshal(e.message(), models.message), 401
    return wrapper

def hash_password(password: str) -> str:
    try:
        hash = bcrypt.generate_password_hash(password).decode('utf-8')
        return hash
    except TypeError:
        raise exc.AuthError('Password must be a utf-8 valid string')

#TODO: Rewrite auth interface as UserSession class.
class UserSession:

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
        except [TypeError, AttributeError]:
            raise exc.AuthError('Invalid Authorization header.')
    
    def _get_token(auth: str) -> str:
        try:
            return auth.replace('Token ', '', 1)
        except [TypeError,  AttributeError]:
            raise exc.AuthError('Invalid Authorization header.')
    
    def _validate_token(token_string: str) -> bool:
        with session_scope() as session:
            try:
                db_interface = DAO(session)
                db_interface.query(token_string)
                if db_interface.data.is_valid():
                    return True
                else: 
                    db_interface.delete()
                    return False
            except exc.SessionError as e:
                raise exc.AuthError(str(e))
    
    #def _refresh_token(token_string: str) -> bool:
    
    def login(header: str) -> Dict:
        try:
         
            if 'Basic' in header:
                username, password = _decode_basic(header)
                with session_scope() as session:
                    db_interface = DAO(session)
                    db_interface.query(username)
                    user_data = db_interface.get_user()
                    if _verify_password(user_data['password_hash'], password):
                        db_interface.assign_token()
                        token = db_interface.data.token
                        db_interface.query(token)
                        return db_interface.data.info()
                    raise exc.AuthError('Invalid username or password.')
    
            elif 'Token' in header:
                token_str = _get_token(header)
                with session_scope() as session:
                    token = db_interface.query_token(token_str, session)
                    token.refresh()
                    return token.info()
            raise exc.AuthError('Invalid authentication method.')
    
        except (exc.SessionError, exc.AuthError) as e:
            raise e
             
    def logout(header: str) -> None:
        try:
    
            token_str = _get_token(header)
            with session_scope() as session:
                db_interface.query(token_str)
                db_interface.delete()
                pass
    
        except (exc.AuthError, exc.SessionError) as e:
            raise e
    
