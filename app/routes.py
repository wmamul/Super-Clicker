from app.api import api
import app.api.account as acc

api.add_resource(acc.Login, '/user/login')
api.add_resource(acc.Register, '/user/register')