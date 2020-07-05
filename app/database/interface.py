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

def query_token(token_string: str, session: Session) -> User:
    token = session.query(Token).filter_by(id=token_string).first()
    if token.is_valid():
        token.refresh()
        return session.query(User).filter_by(username=token.user_ref).first()
    else:
        raise DatabaseError('Token does not exist or expired.')

def create_token(session: Session, user: Optional[User] = None): 
    if user:
        query_user(user, session)
        token = Token(user)
        session.add(token)
    else:
        dummy_user = { 'username': lambda: str(uuid.uuid4())[0:18],
                'email': lambda: str(uuid.uuid4()),
                'password': lambda: str(uuid.uuid4()) }
        create_user(dummy_user, session)
        user = query_user(dummy_user['username'], session)
        token = Token(user)
        session.add(token)

def check_token(token_string: str, session: Session) -> bool:
    token = session.query(Token).filter_by(id=token_string).first()
    if token.is_valid():
        token.refresh()
        return True
    return False

def delete_token(user: User, session: Session):
    token = query_token(user, session)
    if token:
        session.delete(token)
