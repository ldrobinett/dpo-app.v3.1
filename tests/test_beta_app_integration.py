"""Actual beta app registration and templates, using only an isolated SQLite DB."""
from app import create_app
from extensions import db
from models import Capability, ManagedStore, Role, Team, TeamMember, User


def test_actual_beta_app_templates_and_migration_history(monkeypatch):
    monkeypatch.setenv('DATABASE_URL', 'sqlite://')
    monkeypatch.setenv('SECRET_KEY', 'isolated-beta-test')
    app = create_app()
    app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    with app.app_context():
        db.create_all()
        store = ManagedStore(id=1, name='Beta fixture', url='https://example.invalid', admin_username='fixture')
        role = Role(name='Manager', store_id=1, capabilities=[Capability(key=k) for k in ('schedule.manage', 'finance.view')])
        db.session.add_all([store, User(id=1, username='manager', password='unused', store_id=1, roles=[role]),
                            Team(id=1, name='Beta team', store_id=1), TeamMember(id=1, name='Beta technician', team_id=1)])
        db.session.commit()
    try:
        client = app.test_client()
        with client.session_transaction() as session:
            session['_user_id'] = 'u:1'
            session['_fresh'] = True
        for path, expected in [('/generate_schedule', b'Replace work schedule'),
                               ('/dashboard', b'No shared store inputs'),
                               ('/manage/initial_setup', b'<form')]:
            response = client.get(path)
            assert response.status_code == 200, (path, response.status_code)
            assert expected in response.data
        runner = app.test_cli_runner()
        heads = runner.invoke(args=['db', 'heads'])
        assert heads.exit_code == 0, heads.output
        history = runner.invoke(args=['db', 'history'])
        assert history.exit_code == 0, history.output
    finally:
        with app.app_context():
            db.session.remove()
            db.drop_all()
