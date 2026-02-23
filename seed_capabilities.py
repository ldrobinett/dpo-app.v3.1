from app import create_app
from extensions import db
from models import Capability

app = create_app()

CAPABILITIES = [
    # Finance
    ("finance.view", "View financial dashboards and forecasts"),
    ("finance.edit", "Edit financial inputs and forecasts"),

    # Route Sheet
    ("routesheet.view", "View route sheet"),
    ("routesheet.edit", "Create and edit repair orders"),
    
    ("schedule.manage", "Manage technician schedules"),


    # Teams / Staff
    ("teams.manage", "Manage teams, technicians, and ASMs"),

    # Work Logs
    ("worklog.manage", "Create and edit work logs"),

    # Users / Admin
    ("users.manage", "Manage users and roles"),
]

with app.app_context():
    for key, description in CAPABILITIES:
        exists = Capability.query.filter_by(key=key).first()
        if not exists:
            db.session.add(Capability(key=key, description=description))

    db.session.commit()
    print("✅ Capabilities seeded")
