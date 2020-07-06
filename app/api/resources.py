from flask import request
from flask_restx import Resource, marshal
from app.api import api, models
from app.database import session_scope, interface as db_interface
from app.users import auth
from app.exceptions import SessionError, AuthError, DatabaseError

@api.route('/login')
class Login(Resource):

    @api.response(200, 'Returns login token', model=models.token)
    @api.response(401, 'Returns detailed error message', model=models.message)
    def get(self): 
        
        authorization = request.headers.get('Authorization')
        if authorization:
            try:
                username, password = auth.decode_basic(authorization)
            except AuthError as e:
                return marshal(e, models.message), 401
            with session_scope() as session:
                try:
                    user = db_interface.query_user(username, session)
                    if auth.verify_password(user.password_hash, password):
                        token = create_token(session, user)
                        return marshal(token.id, models.token), 200
                except [DatabaseError, AuthError] as e:
                    return marshal(e, models.message), 401

@api.route('/logout')
class Logout(Resource):

    def get(self):
        db_interface.delete_token(current_user)
        logout_user()

@api.route('/user/register')
class Register(Resource):

    @api.response(400, 'Returns detailed error message', model=models.message)
    def post(self):

        try:
            data = request.get_json()
            data['password'] = auth.hash_password(data['password'])
            with session_scope() as session:
                db_interface.create_user(data, session)
            return 201
        except SessionError as e:
            return marshal(e, models.message), 400

@api.route('/user/<string:username>')
class Profile(Resource):

    @api.response(200, 'Returns user model', model=models.user)
    @api.response(404, 'Returns detailed error message', model=models.message)
    @auth.token_required
    def get(self, username):

        with session_scope() as session:
            try:
                user = db_interface.query_user(username, session)
                return marshal(user.info(), models.user), 200
            except DatabaseError as e:
                return marshal(e, models.message), 404
    
    @api.response(400, 'Returns detailed error message', model=models.message)
    def put(self):

        try:
            data = request.get_json()
            if 'password' in data:
                data['password'] = auth.hash_password(data['password'])
            with session_scope() as session:
                db_interface.update_user(current_user, data)
            return 200
        except SessionError as e:
            return marshal(e, models.message), 400
