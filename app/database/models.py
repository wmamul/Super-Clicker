from typing import Dict
from datetime import datetime, timedelta
from sqlalchemy import (Column,
                        Integer,
                        String,
                        DateTime,
                        ForeignKey,
                        Sequence)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
import uuid

EXP_TIME = 3600 # token expiry time in seconds

Base = declarative_base()

class User(Base):

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
    token = Column(String(36), ForeignKey('tokens.id'), unique=True)
    progress = relationship('Progress', uselist=False, backref='users')

    def __init__(self, data: Dict):
        self.username = data['username']
        self.email = data['email']
        self.password_hash = data['password']

    def __repr__(self) -> str:
        return '<User(username=%s, email=%s, image=%s, last_login=%s, password_hash=%s)>' % (
                self.username, self.email, self.image, self.last_login, self.password_hash)

    def info(self) -> Dict:
        user = (('username', self.username),
                ('email', self.email),
                ('image', self.image),
                ('password', self.password_hash),
                ('last_login', self.last_login),
                ('token', self.token))
        return dict(user)

class Token(Base):

    __tablename__ = 'tokens'

    id = Column(String(36), Sequence('token_id_seq'), default=lambda:
         str(uuid.uuid4()), unique=True, primary_key=True)
    expiry = Column(DateTime, default=(datetime.utcnow() +
             timedelta(seconds=EXP_TIME)))
    user_ref = relationship('User', backref=backref('tokens',
        cascade='all, delete-orphan', single_parent=True), lazy='joined', uselist=False)

    def __init__(self, user: User):
        self.user_ref = user.id

    def __str__(self) -> str:
        return self.id

    def info(self) -> Dict:
        token = (('token', self.id),
                 ('exp', self.expiry))
        return dict(token)

    def is_valid(self) -> bool:
        if self.expiry > datetime.utcnow():
            return True
        return False

    def refresh(self) -> None:
        self.expiry = datetime.utcnow() + timedelta(seconds=EXP_TIME)

#TODO: Define progress table
class Progress(Base):

    __tablename__ = 'progress'

    id = Column(String(36), default=lambda: str(uuid.uuid4()), unique=True,
            primary_key=True)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
