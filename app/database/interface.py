from typing import Dict, Optional
from . import Session
from app.database.models import User, Token
from app.exceptions import DatabaseError, SessionError
import uuid

def query_user(username: str, session: Session) -> User:
    user = session.query(User).filter_by(username=username).first()
    if user:
        return user
    else:
        raise DatabaseError('User does not exist: ' + username)

def create_user(data: Dict, session: Session):
    try:
        new_user = User()
        new_user.username = data['username']
        new_user.email = data['email']
        new_user.password_hash = data['password']
        session.add(new_user)
    except KeyError as e:
        raise SessionError('Insufficient data to create a user. ' + str(e))

def update_user(username: str, data: Dict, session: Session):
    try:
        user = session.query(User).filter_by(username=username).first()
        user.username = data['username']
        user.email = data['email']
        user.image = '../../media/' + data['image']
        user.password_hash = data['password']
    except KeyError as e:
        raise SessionError('Insufficient data to update user info. ' + str(e)) 

def query_token(user: User, session: Session) -> Token:
    token = session.query(Token).filter_by(user_ref=user.username).first()
    if token and token.is_valid():
        return token
    else:
        raise DatabaseError('Token does not exist or expired.')

def create_token(session: Session, user: Optional[User] = None): 
    if user:
        query_user(user, session)
        token = Token(user)
        session.add(token)
        return token
    else:
        dummy_user = { 'username': lambda: str(uuid.uuid4())[0:18],
                'email': lambda: str(uuid.uuid4()),
                'password': lambda: str(uuid.uuid4()) }
        create_user(dummy_user, session)
        user = query_user(dummy_user['username'], session)
        token = Token(user)
        session.add(token)
        return token

def refresh_token(user: User, session: Session):
    token = session.query(Token).filter_by(user_ref=user.username).first()
    if token and token.is_valid():
        token.refresh()
    else:
        raise DatabaseError('Token does not exist or expired.')

def delete_token(user: User, session: Session):
    token = query_token(user, session)
    if token:
        session.delete(token)
