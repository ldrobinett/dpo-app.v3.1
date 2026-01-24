from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate  # <-- NEW: Import Flask-Migrate

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'login'
bcrypt = Bcrypt()
migrate = Migrate()  # <-- NEW: Initialize the Migrate object