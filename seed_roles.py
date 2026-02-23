from app import create_app
from extensions import db
from models import Role, Capability

app = create_app()
with app.app_context():

    caps = {c.key: c for c in Capability.query.all()}

    ROLE_MAP = {
        "Admin": [
            "teams.manage",
            "users.manage",
            "routesheet.view",
            "routesheet.edit",
            "worklog.manage",
            "finance.view",
            "schedule.manage",
        ],
        "Manager": [
            "teams.manage",
            "routesheet.view",
            "routesheet.edit",
            "worklog.manage",
            "finance.view",
        ],
        "Advisor": [
            "routesheet.view",
            "routesheet.edit",
        ],
        "Technician": [
            "routesheet.view",
        ],
    }

    for name, keys in ROLE_MAP.items():
        role = Role.query.filter_by(name=name, store_id=1).first()
        if not role:
            role = Role(name=name, store_id=1)
            db.session.add(role)

        role.capabilities = [caps[k] for k in keys]

    db.session.commit()
    print("Roles created.")
