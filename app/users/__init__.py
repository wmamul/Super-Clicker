from . import auth
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.user_loader(auth.load_user)
