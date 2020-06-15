from flask import Flask
from app.api import api
from app.database import db, login_manager

app = Flask(__name__)
app.config['SECRET_KEY'] = '3Ri5/uVHnSzpIg0Zn2cSDuPkwDp9skUy1RClPzevYS8='
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

api.init_app(app)
db.init_app(app)
login_manager.init_app(app)