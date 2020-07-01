from datetime import datetime, timedelta
from . import db
import uuid

EXP_TIME = 3600 # token expiry time in seconds

class User(db.Model):

    id = db.Column(db.String(36), default=lambda: str(uuid.uuid4()), unique=True, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image = db.Column(db.String(100),
                       nullable=False,
                       default='../../media/default_image.jpg')
    last_login = db.Column(db.DateTime(), unique=False, nullable=False, default=datetime.utcnow())
    password_hash = db.Column(db.String(60), nullable=False)
#    progress = db.relationship('Progress', backref='user', lazy=True)

    def __repr__(self):
        user = (self.username, self.email, self.image, self.id)
        print(f"User: {user}")

    def info(self):
        user = (("username", self.username),
                ("email", self.email),
                ("image", self.image),
                ("id", self.id))
        return dict(user)

class Token(db.Model):

    id = db.Column(db.Integer(), default=lambda: str(uuid.uuid4()), unique=True, primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime(), default=datetime.utcnow())
    expiry = db.Column(db.DateTime(), default=datetime.utcnow() + timedelta(seconds=EXP_TIME))

    def __init__(self, user):
        self.user_id = user.id

    def is_valid(self):
        if self.expiry > datetime.utcnow():
            return True
        return False

    def refresh(self):
        self.expiry = datetime.utcnow() + timedelta(seconds=EXP_TIME)
'''
#TODO: Define progress table
class Progress(db.Model):

    id = db.Column(db.Integer(), default=lambda: str(uuid.uuid4()), unique=True, primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
'''
