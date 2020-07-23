from flask_restx import Api
from .authentication import api as auth_ns
from .user import api as user_ns

api = Api(
        title='Super-Clicker API',
        version='0.1')


api.add_namespace(auth_ns)
api.add_namespace(user_ns)
