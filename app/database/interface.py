import uuid
from typing import Dict, Optional
from . import Session
from app.database.models import User, Token
from app.exceptions import SessionError

class DAO:

    data = None
    session = None

    def __init__(self, session: Session):
        self.session = session

    def query(self, query: str):
        user = self.session.query(User).filter_by(username=query).first()
        token = self.session.query(Token).filter(Token.id == query).first()
        if user:
            self.data = user
        elif token:
            self.data = token
        else:
            raise SessionError('Query does not match any database entry: ' + query)
    
    def update_user(self, updated_data: Dict):
        if isinstance(self.data, User):
            try:
                self.data.username = updated_data['username']
                self.data.email = updated_data['email']
                self.data.image = '../../media/' + updated_data['image']
                self.data.password_hash = udpated_data['password']
            except KeyError as e:
                raise SessionError('Insufficient data to update user info. ' + str(e)) 
    
    def new_user(self, credentials: Dict):
        try:
            self.data = User(credentials)
            self.session.add(self.data)
        except KeyError as e:
            raise SessionError('Insufficient data to create a user. ' + str(e))
        
    def delete(self):
        if self.data:
            self.session.delete(self.data)
        else:
            raise SessionError('Nothing queried.')

    @property
    def token(self):
        if isinstance(self.data, Token):
            return self.data.info()
        else:
            return None

    @property
    def user(self):
        if isinstance(self.data, User):
            return self.data.info()
        else:
            return None

    def assign_token(self):
        if isinstance(self.data, User) and not self.data.token:
            token = Token(self.data)
            self.session.add(token)
            self.session.commit()
            self.data.token = token.id
        elif isinstance(self.data, User) and self.data.token:
            raise SessionError('User already logged in. Login using Token to refresh it.')
        else:
            raise SessionError('Queried object is not an instance of User object.')
