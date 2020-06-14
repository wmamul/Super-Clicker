from flask import make_response, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from flask_restx import Resource
from app.api import api, parser
import app.database.interface as db_interface
from app.users import auth
from app.exceptions import DatabaseError

@api.route('/login')
class Login(Resource):
    def get(self):        
        try:
            args = parser.parse_args()
            data = request.get_json()
            if args['key']:
                user = db_interface.query_user(args['key'])
                login_user(user)
                token = auth.encode_token(db_interface.create_token(user))
                return make_response({'message': 'User succesfully logged in', 'JWT': token}, 200)
            elif auth.password_is_valid(data['username'], data['password']):
                user = db_interface.query_user(data['username'])
                login_user(user)
                token = db_interface.create_token(user)
                return make_response({'message': 'User succesfully logged in', 'JWT': token}, 200)
        except DatabaseError as e:
            return make_response({'message': e.message}, 400)

@api.route('/logout')
class Logout(Resource):
    @login_required
    def get(self):
        db_interface.delete_token(current_user)
        logout_user()

@api.route('/user/register')
class Register(Resource):
    def post(self):
        try:
            data = request.get_json()
            db_interface.create_user(data)
            return make_response({'message': 'User successfully created.'}, 200)
        except DatabaseError as e:
            return make_response({'message': e.message}, 400)

@api.route('/user/<string:user_id>')        
class Profile(Resource):
    @login_required
    def get(self):
        user = db_interface.query_user(current_user)
        return make_response(jsonify(user.info), 200)
        
    @login_required
    def put(self):
        try:
            data = request.get_json()
            db_interface.update_user(current_user, data)
            return make_response({'message': 'User data sucessfully updated.'}, 200)
        except DatabaseError as e:
            return make_response({'message': e.message}, 400)