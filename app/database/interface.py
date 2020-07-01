from typing import Dict
from app.database import db
from app.database.models import User, Token
from app.exceptions import DatabaseError, AuthError
from sqlalchemy.exc import IntegrityError
import uuid

def query_user(username: str) -> User:
    user = User.query.get(username)
    if user:
        return user
    else:
        raise DatabaseError('User does not exist: ' + username)

def create_user(data: Dict):
    try:
        new_user = User()
        new_user.username = data['username']
        new_user.email = data['email']
        new_user.password_hash = data['password']
    except KeyError as e:
        raise DatabaseError('Insufficient data to create a user. ' + str(e))
    try:
        db.session.add(new_user)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        raise DatabaseError('DB-API raised an IntegrityError. Please check integrity of provided data. ' + str(e))

def update_user(username: str, data: Dict):
    try:
        updated_user = query_user(user)
        updated_user.username = data['username']
        updated_user.email = data['email']
        updated_user.image = '../../media/' + data['image']
        updated_user.password_hash = data['password']
    except KeyError as e:
        raise DatabaseError('Insufficient data to update user info. ' + str(e))
    try:
        db.session.add(updated_user)
        db.session.commit()
    except IntegirtyError as e:
        db.session.rollback()
        raise DatabaseError('DB-API raised an IntegrityError. Please check integrity of provided data. ' + str(e))

def query_token(user_id: int) -> Token:
    token = Token.query.get(user_id)
    if token:
        return token
    else:
        raise DatabaseError('Token does not exist.')
    
'''
    if user exists, return jwt for auth
    if user does not exist, create a guest user to save progress
    and return jwt for auth.
    user then can provide randomly created uid in the future
    to regain their progress
'''

def create_token(user=None) -> Token:
    if user:
        token = Token(user)
        db.session.add(token)
        db.session.commit()
        return query_token(user.id)
    else:
        random_user = { 'username': lambda: str(uuid.uuid4())[0:18],
                        'email': lambda: str(uuid.uuid4()),
                        'password': lambda: str(uuid.uuid4()) }
        create_user(random_user)
        new_user = query_user(random_user['username'])
        token = Token(new_user)
        db.session.add(token)
        db.session.commit()
        return query_token(new_user.id)

def delete_token(user):
    token = query_token(user.id)
    db.session.delete(token)
    db.session.commit()
