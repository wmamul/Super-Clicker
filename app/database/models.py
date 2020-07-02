from typing import Dict
from datetime import datetime, timedelta
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Sequence
from flask_login import UserMixin
import uuid

EXP_TIME = 3600 # token expiry time in seconds

Base = declarative_base()

class User(Base, UserMixin):

    __tablename__ = 'users'

    id = Column(String(36), Sequence('user_id_seq'), default=lambda:
         str(uuid.uuid4()), unique=True, primary_key=True)
    username = Column(String(20), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    image = Column(String(100), nullable=False,
            default='../../media/default_image.jpg')
    last_login = Column(DateTime, unique=False, nullable=False,
                 default=datetime.utcnow())
    password_hash = Column(String(60), nullable=False)
#    token = relationship('Token', backref='user', lazy=True)
#    progress = relationship('Progress', backref='user', lazy=True)

    def __repr__(self) -> str:
        return '<User(username=%s, email=%s, image=%s, last_login=%s, password_hash=%s)>' % (
                self.username, self.email, self.image, self.last_login, self.password_hash)

    def info(self) -> Dict:
        user = (('username', self.username),
                ('email', self.email),
                ('image', self.image),
                ('id', self.id))
        return dict(user)

class Token(Base):

    __tablename__ = 'tokens'

    id = Column(String(36), Sequence('token_id_seq'), default=lambda:
         str(uuid.uuid4()), unique=True, primary_key=True)
    user_id = Column(String(36), ForeignKey('user.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow())
    expiry = Column(DateTime, default=datetime.utcnow() +
             timedelta(seconds=EXP_TIME))

    def __init__(self, user: User):
        self.user_id = user.id

    def is_valid(self) -> bool:
        if self.expiry > datetime.utcnow():
            return True
        return False

    def refresh(self) -> None:
        self.expiry = datetime.utcnow() + timedelta(seconds=EXP_TIME)
'''
#TODO: Define progress table
class Progress(Base):

    id = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True,
    primary_key=True)
    user_id = Column(String(36), ForeignKey('user.id'), nullable=False)
'''
