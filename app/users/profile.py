from flask import jsonify
from app import db, bcrypt
from app.database.models import User
from app.exceptions import DatabaseError


def create_profile(data):
    try:
        new_user = User()
        new_user.username = data['username']
        new_user.email = data['email']
        new_user.password_hash = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        db.session.add(new_user)
        db.session.commit()
    except KeyError as e:
        raise DatabaseError('Insufficient data to create a user. Missing data: ' + str(e))

def profile_info(username):
    user = User.query.get(username)
    if not user:
        raise DatabaseError('User does not exist: ' + username)
    return user.info()