import logging
import os

from flask import Flask, redirect, request, url_for
from flask_login import current_user
from flask_migrate import Migrate

from extensions import db, login_manager, bcrypt
from models import User, OperatorUser


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # -------------------------------------------------
    # Core config
    # -------------------------------------------------
    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY", "dev-insecure-key-change-me"
    )

    # Ensure instance folder exists (CRITICAL on Windows)
    os.makedirs(app.instance_path, exist_ok=True)

    # -------------------------------------------------
    # Database config
    # -------------------------------------------------
    database_url = os.environ.get("DATABASE_URL")

    if database_url:
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    else:
        db_path = os.path.join(app.instance_path, "site.db")
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # -------------------------------------------------
    # Cookie / session hardening
    # -------------------------------------------------
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["REMEMBER_COOKIE_HTTPONLY"] = True
    app.config["REMEMBER_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"] = (
        os.environ.get("SESSION_COOKIE_SECURE", "false").lower() == "true"
    )

    # -------------------------------------------------
    # Extensions
    # -------------------------------------------------
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    migrate = Migrate(app, db)

    # -------------------------------------------------
    # Flask-Login config
    # -------------------------------------------------
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        if not user_id:
            return None

        try:
            # New format: "op:1" or "u:1"
            if isinstance(user_id, str) and ":" in user_id:
                prefix, raw_id = user_id.split(":", 1)
                pk = int(raw_id)

                if prefix == "op":
                    return db.session.get(OperatorUser, pk)
                if prefix == "u":
                    return db.session.get(User, pk)

                return None

            # Backward compatibility
            return db.session.get(User, int(user_id))

        except Exception:
            logging.getLogger(__name__).warning(
                "Invalid user_id for load_user: %s", user_id
            )
            return None

    # -------------------------------------------------
    # IMPORTANT: Correct unauthorized redirect handling
    # -------------------------------------------------
    @login_manager.unauthorized_handler
    def unauthorized():
        path = request.path or ""

        if path.startswith("/operator"):
            return redirect(url_for("operator.login", next=path))

        return redirect(url_for("auth.login", next=path))

    # -------------------------------------------------
    # Blueprints
    # -------------------------------------------------
    from blueprints.main import main_bp
    from blueprints.auth import auth_bp
    from blueprints.teams import teams_bp
    from blueprints.schedule import schedule_bp
    from blueprints.finance import finance_bp
    from blueprints.worklog import worklog_bp
    from blueprints.labor_matrix import labor_matrix_bp
    from blueprints.routesheet import routesheet_bp
    from blueprints.calculators import calculators_bp
    from blueprints.onboarding import onboarding_bp
    from blueprints.reconciliation import reconciliation_bp
    from blueprints.operator import operator_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(teams_bp)
    app.register_blueprint(schedule_bp)
    app.register_blueprint(finance_bp)
    app.register_blueprint(worklog_bp)
    app.register_blueprint(labor_matrix_bp)
    app.register_blueprint(routesheet_bp)
    app.register_blueprint(calculators_bp)
    app.register_blueprint(onboarding_bp)
    app.register_blueprint(reconciliation_bp)
    app.register_blueprint(operator_bp)

    return app


# -------------------------------------------------
# Run directly (dev only)
# -------------------------------------------------
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
