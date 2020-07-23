from flask_restx import Api, Namespace

api = Api()

from . import resources

auth_ns = Namespace('Authentication',
        descreption='Authentication and authoriazation methods.',
        path='/', ordered=True)
auth_ns.add_resource(resources.Login)
auth_ns.add_resource(resources.Logout)

user_ns = Namespace('User', description='Methods related to logged in user.',
        path='/user', ordered=True)
user_ns.add_resource(resources.Register)
user_ns.add_resource(resources.User)
