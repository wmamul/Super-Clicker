from flask import make_response, request, jsonify
from flask_restx import Resource
from app.api import api, parser
import app.database.interface as db_interface
from app.users import auth
from app.exceptions import DatabaseError, AuthError

@api.route('/login')
class Login(Resource):
    def get(self):        
        try:
            args = parser.parse_args()
            data = request.get_json()
            if args['key']:
                pass
#                token = 
            elif auth.password_is_valid(data['username'], data['password']):
                user = db_interface.query_user(data['username'])
                token = db_interface.create_token(data['username'])
                #TODO: This is wrong
                return make_response({'JWT' : token.decode('utf-8')}, 200)
        except DatabaseError as e:
            return make_response({'message': e.message}, 400)

@api.route('/user/register')
class Register(Resource):
    def post(self):
        try:
            args = parser.parse_args()
            db_interface.create_user(args)
            return make_response({'message': 'User successfully created.'}, 200)
        except DatabaseError as e:
            return make_response({'message': e.message}, 400)

@api.route('/user/<string:user_id>')        
class Profile(Resource):
    @auth.token_required
    def get(self, user_id):
        try:
            user = profile.profile_info(user_id)
            return make_response(jsonify(user), 200)
        except DatabaseError as e:
            return make_response({'message': e.message}, 404)
        
    @auth.token_required
    def put(self):
        pass
        #TODO: Update user profile info
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        