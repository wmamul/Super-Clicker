import uuid
from typing import Dict, Optional
from . import Session
from app.database.models import User, Token
from app.exceptions import SessionError

class DAO:

    session = None

    def __init__(self, session: Session):
        self.session = session
        _user = None
        _token = None
        _progress = None

    def query(self, query: str):
        """
        Method queries database by username or login token and places
        associated data inside the object.
        """

        user = self.session.query(User).filter_by(username=query).first()
        token = self.session.query(Token).filter_by(id=query).first()
        if user:
            self.user = user
            self.token = self.session.query(Token).filter_by( \
                    user_ref=user).first()

        elif token:
            self.user = token.user_ref
            self.token = token

        else:
            raise SessionError('Query does not match any database entry: ' \
                    + query)

    def update_user(self, updated_data: Dict):
        """
        Update user entry in database with provided updated_data.
        """

        if isinstance(self.user, User):
            try:
                self.user.username = updated_user['username']
                self.user.email = updated_data['email']
                self.user.image = '../../media/' + updated_data['image']
                self.user.password_hash = udpated_data['password']

            except KeyError as e:
                raise SessionError('Insufficient data to update user info. ' \
                        + str(e)) 

    def new_user(self, credentials: Dict):
        """
        Create new user database entry.
        """

        try:
            self.user = User(credentials)
            self.session.add(self.user)

        except KeyError as e:
            raise SessionError('Insufficient data to create a user. ' + str(e))


    @property
    def token(self):
        if self._token and isinstance(self._token, Token):
            return self._token.info()

        return None

    @token.setter
    def token(self, token: Token):
        if isinstance(token, Token):
            self._token = token
            self._user.token = token.id
        else:
            self._token = None

    @token.deleter
    def token(self):
        if self.user and self.token:
            self.session.delete(self._token)
            del self._token
            del self._user.token

        else:
            raise SessionError('Nothing queried.')

    @property
    def user(self):
        if self._user and isinstance(self._user, User):
            return self._user.info()

        return None

    @user.setter
    def user(self, user: User):
        if isinstance(user, User):
            self._user = user
        else:
            self._user = None

    @user.deleter
    def user(self):
        if isinstance(self._user, User):
            self.session.delete(self._user)
            del self._token
            del self._user

    def assign_token(self):
        """
        Create new login token and assign it to a user's account.
        """

        if self.user and not self.token:
            self.token = Token(self._user)
            self.session.add(self._token)
            self.session.commit()
            self._user.token = self._token.id
            self._user.record_login()

        elif self.user and self.token:
            del self.token
            self.assign_token()

        else:
            raise SessionError('Nothing queried.')

    def refresh_token(self):
        """
        Refresh user's login token.
        """

        if self.user and self.token and self._token.is_valid():
            self._token.refresh()

        else:
            raise SessionError('User does not have a token assigned or \
                    token expired.')
