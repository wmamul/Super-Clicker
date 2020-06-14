from flask_restx import Api
from flask_restx import reqparse

api = Api()

parser = reqparse.RequestParser()
parser.add_argument('key')