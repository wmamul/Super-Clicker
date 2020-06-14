from app import app
from app.api import api
import app.api.account as acc

app.run(host='0.0.0.0', port=5000, debug=True)
