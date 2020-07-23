from flask import request
from flask_restx import Resource, Namespace, fields, marshal
from app.users import auth
import app.exceptions as exc

#
# Namespace declaration
#

api = Namespace('Authentication', description='User authentication endpoints',
        path='/')

#
# Namespace models
#

message = api.model("Message", {
    "message": fields.String(max_length=255)
    })

token = api.model("Token", {
    "token": fields.String(max_length=40),
    "exp": fields.DateTime()
    })

#
# Namespace resources
#

@api.route('/login')
class Login(Resource):

    @api.response(200, 'Authentication successful.', model=token)
    @api.response(401, 'Authentication failed.')
    @api.param('Authorization',
            description="'Basic username:password' base64 encoded or 'Token token'.",
            _in='header')
    def get(self): 

        try:
            auth_header = request.headers.get('Authorization')
            token = auth.login(auth_header)
            return marshal(token, token), 200

        except (exc.SessionError, exc.AuthError):
            return 401

@api.route('/logout')
class Logout(Resource):

    @api.response(200, 'User successfully logged out.')
    @api.response(401, 'Authentication failed.')
    @api.param('Authorization', description="Token + user's token", _in='header')
    def get(self):

        try:
            auth_header = request.headers.get('Authorization')
            auth.logout(auth_header)

        except (exc.SessionError, exc.AuthError):
            return 401

