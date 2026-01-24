from flask import Flask
from flask_migrate import Migrate
from extensions import db, login_manager, bcrypt
from models import User
import os
import traceback 
import sys 

def create_app():
    """
    Application factory function.
    """
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = 'a-very-long-and-random-secret-key-for-testing-12345!'

    # === Database Config ===
    project_dir = os.path.dirname(os.path.abspath(__file__)) 
    database_path = os.path.join(project_dir, 'site.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
    
    # --- Initialize Extensions ---
    db.init_app(app)
    bcrypt.init_app(app) 
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    Migrate(app, db)

    # === [UPDATED] USER LOADER ===
    @login_manager.user_loader
    def load_user(user_id):
        try:
            # Simple print for debugging
            print(f"--- DEBUG: load_user called for user_id: {user_id} ---", file=sys.stderr)
            sys.stderr.flush()
            return User.query.get(int(user_id))
        except Exception as e:
            print(f"---! CRITICAL ERROR IN load_user: {e} !---", file=sys.stderr) 
            print(traceback.format_exc(), file=sys.stderr)
            sys.stderr.flush()
            return None
    # === [END UPDATE] ===

    # --- Import and Register Blueprints ---
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
    # [REMOVED] from blueprints.admin import admin_bp 

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
    # [REMOVED] app.register_blueprint(admin_bp) 

    return app

# This part remains separate from create_app
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
