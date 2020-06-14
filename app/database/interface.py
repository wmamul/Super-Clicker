from app import db, bcrypt
from app.database.models import User, Token
from app.exceptions import DatabaseError
import uuid

def query_user(username):
    user = User.query.get(username)
    if user:
        return user
    else:
        raise DatabaseError('User does not exist: ' + username)

def create_user(data):
    try:
        new_user = User()
        new_user.username = data['username']
        new_user.email = data['email']
        new_user.password_hash = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        db.session.add(new_user)
        db.session.commit()
    except KeyError as e:
        raise DatabaseError('Insufficient data to create a user. Missing data: ' + str(e))

def query_token(user_id):
    token = Token.query.get(user_id)
    if token:
        return token.id
    else:
        raise DatabaseError('Token does not exist.')
    
'''
    if user exists, return jwt for auth
    if user does not exist, create a guest user to save progress
    and return jwt for auth.
    user then can provide randomly created uid in the future
    to regain their progress
'''
def create_token(username=None):
    if username:
        user = query_user(username)
        token = Token(user.id)
        db.session.add(token)
        db.session.commit()
        return query_token(user.user_id)
    else:
        random_user = { 'username': lambda: str(uuid.uuid4())[0:18],
                        'email': lambda: str(uuid.uuid4()),
                        'password': lambda: str(uuid.uuid4()) }
        create_user(random_user)
        new_user = query_user(random_user['username'])
        token = Token(new_user.id)
        db.session.add(token)
        db.session.commit()
        return query_token(new_user.id)
