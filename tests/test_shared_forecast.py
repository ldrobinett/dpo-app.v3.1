"""Isolated route tests. No application startup, external services, or live DB."""
from datetime import date
from pathlib import Path
from unittest.mock import patch
import pytest
from flask import Flask
from flask_login import LoginManager
from jinja2 import ChoiceLoader, DictLoader
from extensions import db
from models import (ManagedStore, User, FinancialInputs, FinancialForecast,
                    StoreForecastInputs, Team, TeamMember, ScheduleEntry)
from blueprints.finance import finance_bp

@pytest.fixture
def app():
    app = Flask(__name__, template_folder=str(Path(__file__).resolve().parents[1] / 'templates'))
    app.config.update(TESTING=True, SECRET_KEY='test-only', SQLALCHEMY_DATABASE_URI='sqlite://',
                      WTF_CSRF_ENABLED=False)
    db.init_app(app)
    login = LoginManager(app)
    login.user_loader(lambda identity: db.session.get(User, int(identity)))
    app.register_blueprint(finance_bp)
    from blueprints.onboarding import onboarding_bp
    app.register_blueprint(onboarding_bp)
    app.jinja_loader = ChoiceLoader([DictLoader({'base.html': '{% block content %}{% endblock %}'}), app.jinja_loader])
    with app.app_context():
        db.create_all()
        db.session.add_all([ManagedStore(id=i, name=f'Store {i}', url='https://example.test', admin_username='admin') for i in (1, 2)])
        db.session.add_all([User(id=i, username=f'user{i}', password='not-a-real-password', store_id=1 if i < 3 else 2) for i in (1, 2, 3)])
        db.session.add_all([FinancialInputs(user_id=1, effective_labor_rate=100, labor_margin=50),
                            FinancialInputs(user_id=2, effective_labor_rate=200, labor_margin=60),
                            FinancialInputs(user_id=3, effective_labor_rate=999)])
        db.session.add(Team(id=1, name='Service', store_id=1))
        db.session.add(TeamMember(id=1, name='Tech', team_id=1, daily_production_objective=10))
        db.session.add(ScheduleEntry(team_member_id=1, date=date.today(), schedule_type='WORK'))
        db.session.commit()
    with patch('utils.permissions.has_capability', return_value=True):
        yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()


def client(app, uid):
    result = app.test_client()
    with result.session_transaction() as session:
        session['_user_id'] = str(uid)
        session['_fresh'] = True
    return result


def inputs(version=0, **overrides):
    result = dict(input_version=str(version), confirm_shared_inputs='yes', elr='150',
                  parts_to_labor_ratio='1', labor_margin='50', parts_margin='40')
    result.update(overrides)
    return result


def test_get_never_writes_and_legacy_sources_are_store_scoped(app):
    response = client(app, 1).get('/dashboard?source=3')
    assert response.status_code == 200
    assert b'user1: saved' in response.data and b'user2: saved' in response.data
    assert b'user3: saved' not in response.data
    with app.app_context():
        assert StoreForecastInputs.query.count() == 0
        assert FinancialForecast.query.count() == 0


def test_preview_elr_is_loaded_under_different_form_name(app):
    response = client(app, 1).get('/dashboard?source=2')
    assert b'value="200.00"' in response.data


def test_save_shared_across_users_preserves_legacy_and_get_cannot_overwrite(app):
    assert client(app, 1).post('/dashboard', data=inputs()).status_code == 302
    second = client(app, 2)
    response = second.get('/dashboard')
    assert b'value="150.00"' in response.data
    with app.app_context():
        assert db.session.get(StoreForecastInputs, 1).version == 1
        assert FinancialInputs.query.filter_by(user_id=1).one().effective_labor_rate == 100
        assert FinancialInputs.query.filter_by(user_id=2).one().effective_labor_rate == 200
        forecast = FinancialForecast.query.one()
        assert forecast.total_gross == 1350
    assert second.post('/dashboard', data=inputs(1, elr='160')).status_code == 302
    assert b'value="160.00"' in client(app, 1).get('/dashboard').data


def test_stale_and_repeated_saves_rejected_without_changes(app):
    c = client(app, 1)
    assert c.post('/dashboard', data=inputs()).status_code == 302
    assert c.post('/dashboard', data=inputs(elr='999')).status_code == 409
    assert c.post('/dashboard', data=inputs(1)).status_code == 302
    assert client(app, 2).post('/dashboard', data=inputs(1, elr='888')).status_code == 409
    with app.app_context():
        assert db.session.get(StoreForecastInputs, 1).values['effective_labor_rate'] == 150
        assert FinancialForecast.query.count() == 1


def test_confirmation_and_version_required(app):
    c = client(app, 1)
    assert c.post('/dashboard', data=inputs(confirm_shared_inputs='')).status_code == 409
    assert c.post('/dashboard', data={'elr': '150'}).status_code == 409
    with app.app_context():
        assert StoreForecastInputs.query.count() == 0


def test_invalid_form_cannot_mutate_shared_or_forecast(app):
    assert client(app, 1).post('/dashboard', data=inputs()).status_code == 302
    response = client(app, 2).post('/dashboard', data=inputs(1, labor_margin='101'))
    assert response.status_code == 200 and b'Inputs were not saved' not in response.data  # base omits flashed messages
    assert b'Number must be between' in response.data
    with app.app_context():
        assert db.session.get(StoreForecastInputs, 1).version == 1
        assert FinancialForecast.query.one().total_gross == 1350


def test_store_isolation_and_zero_schedule_save(app):
    assert client(app, 1).post('/dashboard', data=inputs()).status_code == 302
    assert client(app, 3).post('/dashboard', data=inputs(elr='999')).status_code == 302
    with app.app_context():
        assert db.session.get(StoreForecastInputs, 1).values['effective_labor_rate'] == 150
        assert db.session.get(StoreForecastInputs, 2).values['effective_labor_rate'] == 999
        assert FinancialForecast.query.filter_by(store_id=2).one().total_gross == 0


def test_validation_error_does_not_refresh_stale_version(app):
    c = client(app, 1)
    assert c.post('/dashboard', data=inputs()).status_code == 302
    assert c.post('/dashboard', data=inputs(1)).status_code == 302
    response = client(app, 2).post('/dashboard', data=inputs(1, labor_margin='101'))
    assert b'name="input_version" value="1"' in response.data
    assert client(app, 2).post('/dashboard', data=inputs(1, labor_margin='50')).status_code == 409


@pytest.mark.parametrize('field,value', [('other_ro_gross', 'nan'), ('parts_allowance', 'inf'), ('elr', 'NaN'), ('other_ro_gross', '1e999')])
def test_nonfinite_values_are_rejected_before_staging(app, field, value):
    assert client(app, 1).post('/dashboard', data=inputs(**{field: value})).status_code == 400
    with app.app_context():
        assert StoreForecastInputs.query.count() == 0
        assert FinancialForecast.query.count() == 0


def test_calculator_defaults_use_shared_store_inputs(app):
    from types import SimpleNamespace
    from blueprints.calculators import get_shop_stats
    assert client(app, 1).post('/dashboard', data=inputs()).status_code == 302
    with app.test_request_context(), patch('blueprints.calculators.current_user', SimpleNamespace(id=2)):
        assert get_shop_stats(1)['elr'] == 150


def test_forecast_failure_rolls_back_staged_inputs(app):
    from sqlalchemy import event
    def fail_forecast(mapper, connection, target):
        raise RuntimeError('simulated forecast storage failure')
    event.listen(FinancialForecast, 'before_insert', fail_forecast)
    try:
        with pytest.raises(RuntimeError, match='simulated'):
            client(app, 1).post('/dashboard', data=inputs())
    finally:
        event.remove(FinancialForecast, 'before_insert', fail_forecast)
    with app.app_context():
        assert StoreForecastInputs.query.count() == 0
        assert FinancialForecast.query.count() == 0


def test_setup_cannot_change_shared_or_legacy_forecast_after_initialization(app):
    c = client(app, 1)
    assert c.post('/dashboard', data=inputs()).status_code == 302
    response = c.get('/manage/initial_setup')
    assert response.status_code == 200
    assert b'read-only here' in response.data and b'value="150.00"' in response.data
    response = c.post('/manage/initial_setup', data={
        'store_name': 'Store 1', 'elr': '999', 'parts_to_labor': '1',
        'labor_margin': '50', 'parts_margin': '40', 'bays_with_lifts': '12',
        **{field: '' for field in ('other_ro_gross', 'unapplied_time_cost',
           'parts_retail_gross', 'wholesale_gross', 'parts_inventory_adjust',
           'parts_allowance', 'purchase_discounts')},
    })
    assert response.status_code == 302
    with app.app_context():
        assert db.session.get(StoreForecastInputs, 1).values['effective_labor_rate'] == 150
        legacy = FinancialInputs.query.filter_by(user_id=1).one()
        assert legacy.effective_labor_rate == 100
        assert legacy.bays_with_lifts == 12
