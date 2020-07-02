from flask import make_response, request, jsonify
from flask_restx import Resource, fields
from app.api import api, parser
import app.database.interface as db_interface
from app.users import auth
from app.exceptions import DatabaseError, AuthError

user_fields = api.model('User', {
    'username': fields.String(min_length=6, max_length=20),
    'password': fields.String(description='Only used in registration endpoint',
        min_length=8, max_length=20),
    'email': fields.String(max_length=120),
    'image': fields.String(max_length=80, desctiption='Profile picture path on the server'),
    'last_login': fields.DateTime()
    })


@api.route('/login')
class Login(Resource):
    def get(self):        
        try:
            args = parser.parse_args()
            data = request.get_json() #TODO: Add guest user case
            if args['key']:
                user = db_interface.query_user(args['key'])
                login_user(user)
                token = auth.encode_token(db_interface.create_token(user))
                return make_response({'message': 'User succesfully logged in',
                    'JWT': token}, 200)
            else:
                user = db_interface.query_user(data['username'])
                if db_interface.check_password(user, data['password']):
                    login_user(user)
                    token = db_interface.create_token(user)
                    return make_response({'message': 'User succesfully logged
                        in', 'JWT': token}, 200)
        except [DatabaseError, AuthError] as e:
            return make_response({'message': e.message}, 400)

@api.route('/logout')
class Logout(Resource):
    def get(self):
        db_interface.delete_token(current_user)
        logout_user()

@api.route('/user/register')
class Register(Resource):
    @api.marshal_with(user_fields)
    def post(self):
        try:
            data = request.get_json()
            data['password'] = auth.hash_password(data['password'])
            db_interface.create_user(data)
            return make_response({'message': 'User successfully created.'},
                    200)
        except DatabaseError as e:
            return make_response({'message': e.message}, 400)

@api.route('/user/<string:username>')
class Profile(Resource):
    @api.marshal_list_with(user_fields)
    def get(self, username):
        user = db_interface.query_user(username)
#        user = db_interface.query_user(current_user)
        return make_response(jsonify(user.info), 200)
        
    @api.marshal_with(user_fields)
    def put(self):
        try:
            data = request.get_json()
            db_interface.update_user(current_user, data)
            return make_response({'message': 'User data sucessfully updated.'},
                    200)
        except DatabaseError as e:
            return make_response({'message': e.message}, 400)
