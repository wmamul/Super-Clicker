from app.database import db, bcrypt
from app.database.models import User, Token
from app.exceptions import DatabaseError, AuthError
import uuid

def hash_password(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')

def check_password(user, password):
    if bcrypt.check_password_hash(user.password_hash, password):
        return True
    raise AuthError('Invalid password.')

def query_user(username):
    user = User.query.get(username)
    if user:
        return user
    else:
        raise DatabaseError('User does not exist: ' + username)

@login_manager.user_loader
def load_user(user_id):
    return query_user(user_id)

def create_user(data):
    try:
        new_user = User()
        new_user.username = data['username']
        new_user.email = data['email']
        new_user.password_hash = hash_password(data['password'])
        db.session.add(new_user)
        db.session.commit()
    except KeyError as e:
        raise DatabaseError('Insufficient data to create a user. Missing data: ' + str(e))

def update_user(user, data):
    try:
        updated_user = query_user(user)
        updated_user.username = data['username']
        updated_user.email = data['email']
        updated_user.image = '../../media/' + data['image']
        updated_user.password_hash = hash_password(data['password'])
        db.session.add(updated_user)
        db.session.commit()
    except KeyError as e:
        raise DatabaseError('Insufficient data to update user info. Missing data: ' + str(e))

def query_token(user_id):
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
def create_token(user=None):
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