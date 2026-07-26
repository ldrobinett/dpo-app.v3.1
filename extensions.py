from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from sqlalchemy import MetaData

from mi_v5.database.naming import NAMING_CONVENTION


db = SQLAlchemy(metadata=MetaData(naming_convention=NAMING_CONVENTION))
login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # IMPORTANT: blueprint-aware
bcrypt = Bcrypt()
migrate = Migrate()

# -------------------------------------------------
# Flask-Login user loader (CRITICAL)
# -------------------------------------------------
from models import User, OperatorUser


@login_manager.user_loader
def load_user(user_id):
    if user_id.startswith("op:"):
        return OperatorUser.query.get(int(user_id.replace("op:", "")))
    elif user_id.startswith("u:"):
        return User.query.get(int(user_id.replace("u:", "")))
    return None
