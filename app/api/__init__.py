from flask import make_response
from app import app
from flask_restx import Api, reqparse
import jwt

api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('key')