from flask import make_response
from app import app
from flask_restplus import Api
import jwt

api = Api(app)