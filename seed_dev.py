from app import create_app
from extensions import db, bcrypt
from models import ManagedStore, User, Role, Capability, OperatorUser

app = create_app()

CAPABILITIES = [
    ("finance.view", "View financial dashboards and forecasts"),
    ("finance.edit", "Edit financial inputs and forecasts"),
    ("routesheet.view", "View route sheet"),
    ("routesheet.edit", "Create and edit repair orders"),
    ("schedule.manage", "Manage technician schedules"),
    ("teams.manage", "Manage teams, technicians, and ASMs"),
    ("worklog.manage", "Create and edit work logs"),
    ("users.manage", "Manage users and roles"),
    ("routes.view", "View route sheet"),
    ("worklog.view", "View work logs"),
    ("schedule.view", "View calendar"),
    ("production.view", "View production"),
    ("calculators.view", "Access calculators"),
    ("manage.view", "Access manage menu"),
    ("onboarding.manage", "Manage onboarding"),
    ]

ROLE_MAP = {
    "Admin": [
        # New system
    "teams.manage",
    "users.manage",
    "routesheet.view",
    "routesheet.edit",
    "worklog.manage",
    "finance.view",
    "finance.edit",
    "schedule.manage",

    # Legacy UI permissions (required for navbar)
    "routes.view",
    "worklog.view",
    "schedule.view",
    "production.view",
    "manage.view",
    "calculators.view",
    "onboarding.manage",
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

with app.app_context():
    print("Seeding development database...")

    # -----------------------------
    # Ensure ManagedStore exists
    # -----------------------------
    # Use URL as stable identifier for dev
    dev_url = "http://127.0.0.1:5001"
    store = ManagedStore.query.filter_by(url=dev_url).first()

    if not store:
        store = ManagedStore(
            name="Dev Store",
            environment="dev",
            tier="beta",
            status="active",
            url=dev_url,
            admin_username="admin",
        )
        store.set_admin_password("password123")  # uses Fernet + env var
        db.session.add(store)
        db.session.commit()
        print("✅ ManagedStore created")
    else:
        store.name = "Dev Store"
        store.environment = "dev"
        store.tier = store.tier or "beta"
        store.status = "active"
        store.admin_username = "admin"
        if not store.admin_password_enc:
            store.set_admin_password("password123")
        db.session.commit()
        print("✅ ManagedStore updated")

    # -----------------------------
    # Seed Capabilities
    # -----------------------------
    for key, description in CAPABILITIES:
        if not Capability.query.filter_by(key=key).first():
            db.session.add(Capability(key=key, description=description))
    db.session.commit()
    print("✅ Capabilities seeded")

    caps = {c.key: c for c in Capability.query.all()}

    # -----------------------------
    # Seed Roles (scoped to managed_store.id)
    # -----------------------------
    for role_name, keys in ROLE_MAP.items():
        role = Role.query.filter_by(name=role_name, store_id=store.id).first()
        if not role:
            role = Role(name=role_name, store_id=store.id)
            db.session.add(role)
            print(f"✅ Role '{role_name}' created")

         # 🔥 Always fully sync capabilities
        role.capabilities.clear()
        role.capabilities = [caps[k] for k in keys if k in caps]

    db.session.commit()
    print("✅ Roles fully synced to Role_Map")

    # -----------------------------
    # Create store-side admin User + attach Admin role
    # -----------------------------
    admin = User.query.filter_by(username="admin", store_id=store.id).first()
    admin_role = Role.query.filter_by(name="Admin", store_id=store.id).first()

    if not admin:
        admin = User(username="admin", store_id=store.id)
        admin.password = bcrypt.generate_password_hash("password123").decode("utf-8")
        if admin_role:
            admin.roles.append(admin_role)
        db.session.add(admin)
        db.session.commit()
        print("✅ Store user created + Admin role assigned (admin / password123)")
    else:
        if admin_role and admin_role not in admin.roles:
            admin.roles.append(admin_role)
            db.session.commit()
            print("✅ Admin role attached to existing user")
        else:
            print("ℹ️ Store user already exists (role ok)")

    # -----------------------------
    # Operator user
    # -----------------------------
    op = OperatorUser.query.filter_by(username="operator").first()
    if not op:
        op = OperatorUser(
            username="operator",
            password_hash=bcrypt.generate_password_hash("password123").decode("utf-8"),
            is_active=True,
        )
        db.session.add(op)
        db.session.commit()
        print("✅ Operator user created (operator / password123)")
    else:
        print("ℹ️ Operator user already exists")

    print("🎉 Development database ready.")