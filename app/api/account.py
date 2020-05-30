from flask import make_response, jsonify
from flask_restplus import Resource, reqparse
from app.api import api
from app.users import auth, profile
from app.exceptions import DatabaseError, AuthError

parser = reqparse.RequestParser()
parser.add_argument('key')

@api.route('/login')
class Login(Resource):
    def get(self):
        
        try:
            token = auth.create_token(data['username'])
            return make_response({'JWT' : token.decode('utf-8')}, 200)
        except DatabaseError as e:
            return make_response({'message': e.message}, 400)

@api.route('/user/register')
class Register(Resource):
    def post(self):
        
        try:
            profile.create_profile(data)
            return make_response({'message': 'User successfully created.'}, 200)
        except DatabaseError as e:
            return make_response({'message': e.message}, 400)

@api.route('/user')        
class Profile(Resource):
    @auth.token_required
    def get(self):
        
        try:
            user = profile.profile_info(data['username'])
            return make_response(jsonify(user), 200)
        except DatabaseError as e:
            return make_response({'message': e.message}, 404)
        
    @auth.token_required
    def put(self):
        
        #TODO: Update user profile info
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        