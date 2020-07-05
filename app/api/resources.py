from flask import request, jsonify
from flask_restx import Resource, fields, marshal
from app.api import api, parser
from app.database import session_scope, interface as db_interface
from app.users import auth
from app.exceptions import SessionError, AuthError, DatabaseError

message_model = api.model("Message", {
    "message": fields.String(max_length=255)
    })

user_model = api.model("User", {
    "username": fields.String(min_length=6, max_length=20),
    "email": fields.String(max_length=120),
    "image": fields.String(max_length=80, desctiption="Profile picture path on the server"),
    "last_login": fields.DateTime(),
    })

user_register = api.model("User registration requirements", {
    "username": fields.String(min_length=6, max_length=20),
    "password": fields.String(min_length=8, max_length=20),
    "email": fields.String(max_length=120)
    })

@api.route('/login')
class Login(Resource):

    def get(self): 
        try:
            args = parser.parse_args()
            data = request.get_json() #TODO: Add guest user case
            if args['key']:
                token_string = auth.decode_token(args['key'])
                with session_scope() as session:
                    token = db_interface.query_token(token_string, session)
                    user = db_interface.query_user(token.user_ref, session)
                    login_user(user)
                return make_response({"message": "User succesfully logged in",
                    "JWT": token}, 200)
            else:
                if auth.check_password(user.username, data['password']):
                    login_user(user)
                    create_token(user)
                    return make_response({"message": "User succesfully logged in",
                         "JWT": token}, 200)
        except [DatabaseError, AuthError] as e:
            return make_response({"message": e.message}, 400)

@api.route('/logout')
class Logout(Resource):

    def get(self):
        db_interface.delete_token(current_user)
        logout_user()

@api.route('/user/register')
class Register(Resource):

    @api.response(400, 'Returns detailed error message', model=message_model)
    def post(self):
        try:
            data = request.get_json()
            data['password'] = auth.hash_password(data['password'])
            with session_scope() as session:
                db_interface.create_user(data, session)
            return 200
        except SessionError as e:
            return marshal(e, message_model), 400

@api.route('/user/<string:username>')
class Profile(Resource):

    @api.response(200, 'Returns user model', model=user_model)
    @api.response(404, 'Returns detailed error message', model=message_model)
    def get(self, username):
        with session_scope() as session:
            try:
                user = db_interface.query_user(username, session)
                return marshal(user.info(), user_model), 200
            except DatabaseError as e:
                return marshal(e, message_model), 404
    
    @api.response(400, 'Returns detailed error message', model=message_model)
    def put(self):
        try:
            data = request.get_json()
            if 'password' in data:
                data['password'] = auth.hash_password(data['password'])
            with session_scope() as session:
                db_interface.update_user(current_user, data)
            return 200
        except SessionError as e:
            return marshal(e, message_model), 400
