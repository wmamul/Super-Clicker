from app import app
from app.api import api
import app.api.account as acc
#import app.api.auth as auth

api.add_resource(acc.Register, '/user/register')
api.add_resource(acc.Login, '/user/login')

app.run(host='0.0.0.0', port=5000, debug=True)
