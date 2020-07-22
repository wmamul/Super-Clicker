from flask import request, jsonify
from flask_restx import Resource, marshal
from app.api import api, models
from app.database import session_scope
from app.database.interface import DAO
from app.users import auth
import app.exceptions as exc

@api.route('/login')
class Login(Resource):

    @api.response(200, 'Authentication successful.', model=models.token)
    @api.response(401, 'Authentication failed.', model=models.message)
    @api.param('Authorization',
            description="'Basic username:password' base64 encoded or 'Token token'.",
            _in='header')
    def get(self): 
        
        try:
            auth_header = request.headers.get('Authorization')
            token = auth.login(auth_header)
            return marshal(token, models.token), 200
        except (exc.SessionError, exc.AuthError) as e:
            return marshal(e.message(), models.message), 401

@api.route('/logout')
class Logout(Resource):

    @api.response(200, 'User successfully logged out.')
    @api.response(401, 'Authentication failed.', model=models.message)
    @api.param('Authorization', description="Token + user's token", _in='header')
    @auth.token_required
    def get(self):

        try:
            auth_header = request.headers.get('Authorization')
            auth.logout(auth_header)
            pass
        except (exc.SessionError, exc.AuthError) as e:
            return marshal(e.message(), models.message), 401

@api.route('/user/register')
class Register(Resource):

    @api.response(200, 'User succesfully created.')
    @api.response(400, 'Bad Request.', model=models.message)
    @api.expect(models.user_register, validate=True)
    def post(self):

        try:
            data = request.get_json()
            if data:
                data['password'] = auth.hash_password(data['password'])
                with session_scope() as session:
                    db_interface = DAO(session)
                    db_interface.new_user(data)
            else:
                raise exc.SessionError('No JSON data provided')
        except exc.SessionError as e:
            return marshal(e.message(), models.message), 400

@api.route('/user/<string:username>')
@api.param('username',
           'User identifier for profile query. Must be authorized and provide login token in request header.')
class Profile(Resource):

    @api.response(200, 'Provides user model.', model=models.user_info)
    @api.response(404, 'User not found.', model=models.message)
    @api.param('Authorization', description="Token + user's token.", _in='header')
    def get(self, username):

        with session_scope() as session:
            try:
                db_interface = DAO(session)
                db_interface.query(username)
                user_info = db_interface.user
                return marshal(user_info, models.user_info), 200
            except exc.SessionError as e:
                return marshal(e.message(), models.message), 404
    
    @api.response(200, 'User profile updated.')
    @api.response(400, 'Bad Request.', model=models.message)
    @api.param('username',
               "User identifier to update authenticated user's profile info.")
    @api.param('Authorization', description="Token + user's token.", _in='header')
    @api.expect(models.user_update, validate=True)
    @auth.token_required
    def put(self, username):

        try:
            data = request.get_json()
            if 'password' in data:
                data['password'] = auth.hash_password(data['password'])
            with session_scope() as session:
                db_interface = DAO(session)
                db_interface.query(username)
                db_interface.update_user(data)

        except exc.SessionError as e:
            return marshal(e.message(), models.message), 400
