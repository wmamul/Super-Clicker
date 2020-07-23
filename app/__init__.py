from flask import Flask
import app.api 
import app.users 

app = Flask(__name__)
app.config['SECRET_KEY'] = '3Ri5/uVHnSzpIg0Zn2cSDuPkwDp9skUy1RClPzevYS8='
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

api.api.init_app(app)
users.bcrypt.init_app(app)
