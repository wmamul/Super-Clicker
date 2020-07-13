import uuid
from typing import Dict, Optional
from . import Session
from app.database.models import User, Token
from app.exceptions import SessionError

def query_user(username: str, session: Session) -> User:
    user = session.query(User).filter_by(username=username).first()
    if user:
        return user
    else:
        raise SessionError('User does not exist: ' + username)

def create_user(data: Dict, session: Session):
    try:
        new_user = User(data)
        session.add(new_user)
    except KeyError as e:
        raise SessionError('Insufficient data to create a user. ' + str(e))

def update_user(user: User, data: Dict, session: Session):
    user = query_user(username, session)
    try:
        user.username = data['username']
        user.email = data['email']
        user.image = '../../media/' + data['image']
        user.password_hash = data['password']
    except KeyError as e:
        raise SessionError('Insufficient data to update user info. ' + str(e)) 

def query_token(token_string: str, session: Session) -> Token:
    token = session.query(Token).filter(Token.id == token_string).first()
    if token:
        return token
    else:
        raise SessionError('Such token does not exist.')

def query_user_by_token(token: Token, session: Session) -> User:
    user = session.query(User).join(Token).filter_by(id=token.id).first()
    if user: 
        return user
    else:
        raise SessionError('Invalid token.')

def create_token(session: Session, user: Optional[User] = None): 
    if user:
        token = Token()
        session.add(token)
        session.commit()
        user.token = token.id
        session.flush()
    else:
        dummy_user = { 'username': lambda: str(uuid.uuid4())[0:18],
                'email': lambda: str(uuid.uuid4()),
                'password': lambda: str(uuid.uuid4()) }
        create_user(dummy_user, session)
        session.commit()
        user = query_user(dummy_user['username'], session)
        token = Token()
        session.add(token)
        session.commit()
        user.token = token.id
        session.flush()
    
def delete_token(token: Token, session: Session):
    try:
        session.delete(token)
    except:
        raise SessionError('Such token does not exist.')
