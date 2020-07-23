from flask import request
from flask_restx import Resource, Namespace, fields, marshal
from app.database import session_scope
from app.database.interface import DAO
from app.users import auth
import app.exceptions as exc

#
# Namespace declaration
#

api = Namespace('User', description='User account endpoints', path='/user')

#
# Namespace models
#

message = api.model("Message", {
    "message": fields.String(max_length=255)
    })

user_register = api.model("Registration", {
    "username": fields.String(min_length=6, max_length=20),
    "password": fields.String(min_length=8, max_length=20),
    "email": fields.String(max_length=120)
    })

user_update = api.inherit("Update user", user_register, {
    "image": fields.String(max_length=80, desctiption="Profile picture path on the server")
    })

user_info = api.inherit("Full user info", user_update, {
    "last_login": fields.DateTime()
    })

#
# Namespace resources
#

@api.route('/register')
class Register(Resource):

    @api.response(200, 'User succesfully created.')
    @api.response(400, 'Bad Request.', model=message)
    @api.expect(user_register, validate=True)
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
            return marshal(e.message(), message), 400

@api.route('/<string:username>')
@api.param('username',
           'User identifier for profile query. Must be authorized and provide login token in request header.')
@api.doc('Query user data from database.')
class User(Resource):

    @api.response(200, 'Success.', model=user_info)
    @api.response(404, 'User not found.')
    @api.param('Authorization', description="Token + user's token.", _in='header')
    @auth.token_required
    def get(self, username):

        with session_scope() as session:
            try:
                db_interface = DAO(session)
                db_interface.query(username)
                return marshal(db_interface.user, user_info), 200

            except exc.SessionError:
                return 404

    @api.response(200, 'User profile updated.')
    @api.response(400, 'Bad Request.', model=message)
    @api.param('Authorization', description="Token + user's token.", _in='header')
    @api.expect(user_update, validate=True)
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
            return marshal(e.message(), message), 400

    @api.response(200, 'User successfuly deleted.')
    @api.response(401, 'Unauthorized.')
    @api.response(404, 'User not found.')
    @api.param('Authorization', description="Token + user's token.", _in='header')
    @auth.token_required
    def delete(self, username):

        with session_scope() as session:
            try:
                db_interface = DAO(session)
                db_interface.query(username)
                del db_interface.user
                return 200

            except exc.SessionError:
                return 401
