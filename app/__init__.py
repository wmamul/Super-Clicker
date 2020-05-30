from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

app = Flask(__name__)

app.config['SECRET_KEY'] = '3Ri5/uVHnSzpIg0Zn2cSDuPkwDp9skUy1RClPzevYS8='
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

bcrypt = Bcrypt()