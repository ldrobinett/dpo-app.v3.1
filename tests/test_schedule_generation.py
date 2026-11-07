"""Real Flask/form/ORM regression tests on a disposable SQLite database only."""

import unittest
from datetime import date, datetime, time, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from flask import Flask
from jinja2 import ChoiceLoader, DictLoader, FileSystemLoader
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects import postgresql

from extensions import db, login_manager
from models import Capability, ManagedStore, Role, ScheduleEntry, Team, TeamMember, User
from blueprints.schedule import schedule_bp
from utils.schedule_generation import plan_recurring_schedule


START = date(2026, 11, 9)  # Monday
END = START + timedelta(days=6)
SHIFT = dict(start_time=time(9), end_time=time(18), lunch_start=None, lunch_end=None, notes='New pattern')


class ScheduleGenerationTests(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).resolve().parents[1]
        self.app = Flask(__name__)
        self.app.config.update(
            SECRET_KEY='isolated-test-only', TESTING=True,
            SQLALCHEMY_DATABASE_URI='sqlite://', WTF_CSRF_ENABLED=False,
        )
        # Render the actual schedule template without unrelated app blueprints.
        self.app.jinja_loader = ChoiceLoader([
            DictLoader({'base.html': '{% for category, message in get_flashed_messages(with_categories=true) %}'
                        '<p class="{{category}}">{{message}}</p>{% endfor %}{% block content %}{% endblock %}'}),
            FileSystemLoader(str(root / 'templates')),
        ])
        db.init_app(self.app)
        login_manager.init_app(self.app)
        self.app.register_blueprint(schedule_bp)
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        db.session.add_all([
            ManagedStore(id=1, name='Honda fixture', url='https://example.invalid/1', admin_username='fixture'),
            ManagedStore(id=2, name='Other store', url='https://example.invalid/2', admin_username='fixture'),
            Team(id=1, name='Blue', store_id=1), Team(id=2, name='Foreign', store_id=2),
            Team(id=3, name='Red', store_id=1),
            TeamMember(id=1, name='One', team_id=1), TeamMember(id=2, name='Two', team_id=1),
            TeamMember(id=3, name='Foreign technician', team_id=2),
            TeamMember(id=4, name='Retired', team_id=1, retired_at=datetime(2026, 10, 1)),
            TeamMember(id=5, name='Red technician', team_id=3),
        ])
        cap = Capability(key='schedule.manage')
        role = Role(name='Schedule Manager', store_id=1, capabilities=[cap])
        db.session.add_all([
            User(id=1, username='manager', password='not-used', store_id=1, roles=[role]),
            User(id=2, username='reader', password='not-used', store_id=1),
        ])
        db.session.commit()
        self.client = self.app.test_client()
        self.login(1)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def login(self, user_id):
        with self.client.session_transaction() as session:
            session['_user_id'] = f'u:{user_id}'
            session['_fresh'] = True

    def entry(self, member=1, day=START, kind='WORK', **changes):
        values = dict(team_member_id=member, date=day, schedule_type=kind,
                      start_time=time(8), end_time=time(17), lunch_start=time(12),
                      lunch_end=time(13), notes='Original')
        values.update(changes)
        row = ScheduleEntry(**values)
        db.session.add(row)
        db.session.commit()
        return row

    def payload(self, **changes):
        values = dict(team='__None', team_member='1', start_date=START.isoformat(),
                      end_date=END.isoformat(), days_of_week=['1', '2', '3', '4', '5'],
                      start_time='09:00', end_time='18:00', lunch_start='', lunch_end='',
                      notes='New pattern', operation='replace', confirm_replace='y')
        values.update(changes)
        return values

    def save(self, **changes):
        return self.client.post('/generate_schedule', data=self.payload(**changes))

    def snapshot(self):
        return [(r.id, r.team_member_id, r.date, r.start_time, r.end_time,
                 r.lunch_start, r.lunch_end, r.notes, r.schedule_type)
                for r in ScheduleEntry.query.order_by(ScheduleEntry.id)]

    def test_changed_weekdays_replace_instead_of_combining_and_repeat_is_idempotent(self):
        for offset in range(5):
            self.entry(day=START + timedelta(days=offset))
        response = self.save()
        self.assertEqual(response.status_code, 302)
        entries = ScheduleEntry.query.order_by(ScheduleEntry.date).all()
        self.assertEqual([e.date.weekday() for e in entries], [1, 2, 3, 4, 5])
        self.assertTrue(all(e.start_time == time(9) and e.lunch_start is None for e in entries))
        state = self.snapshot()
        self.assertEqual(self.save().status_code, 302)
        self.assertEqual(self.snapshot(), state)
        page = self.client.get(response.location)
        self.assertIn(b'1 added, 4 updated, 1 removed', page.data)
        self.assertIn(b'Schedule Entries in the Selected Range', page.data)
        self.assertEqual(self.snapshot(), state)

    def test_add_mode_preserves_old_days_and_shift_times(self):
        for offset in range(5):
            self.entry(day=START + timedelta(days=offset))
        self.assertEqual(self.save(operation='add', confirm_replace='').status_code, 302)
        entries = ScheduleEntry.query.order_by(ScheduleEntry.date).all()
        self.assertEqual([e.date.weekday() for e in entries], list(range(6)))
        self.assertEqual([e.start_time for e in entries], [time(8)] * 5 + [time(9)])

    def test_default_action_is_add_missing_not_replace(self):
        self.entry()
        payload = self.payload()
        payload.pop('operation')
        payload.pop('confirm_replace')
        self.assertEqual(self.client.post('/generate_schedule', data=payload).status_code, 302)
        self.assertEqual(ScheduleEntry.query.filter_by(date=START).one().start_time, time(8))

    def test_shift_only_edit_updates_existing_row_in_place(self):
        row = self.entry()
        row_id = row.id
        self.assertEqual(self.save(days_of_week=['0'], end_date=START.isoformat()).status_code, 302)
        saved = db.session.get(ScheduleEntry, row_id)
        self.assertEqual(saved.start_time, time(9))
        self.assertEqual(saved.end_time, time(18))
        self.assertEqual(saved.notes, 'New pattern')
        self.assertEqual(ScheduleEntry.query.count(), 1)

    def test_exceptions_on_selected_and_deselected_days_are_preserved(self):
        exceptions = []
        for offset, kind in enumerate(['PTO', 'TRAINING', 'HOLIDAY', 'OFF', 'CUSTOM']):
            exceptions.append(self.entry(day=START + timedelta(days=offset), kind=kind))
        before = self.snapshot()
        self.assertEqual(self.save().status_code, 302)
        self.assertEqual(self.snapshot()[:5], before)
        self.assertEqual(ScheduleEntry.query.count(), 6)  # Only Saturday is new.

    def test_team_replacement_excludes_other_teams_stores_retired_and_outside_dates(self):
        for member in [1, 2, 3, 4, 5]:
            self.entry(member=member)
        self.entry(day=START - timedelta(days=1))
        self.entry(day=END + timedelta(days=1))
        unaffected = [row for row in self.snapshot() if row[1] in {3, 4, 5} or row[2] not in {START}]
        self.assertEqual(self.save(team='1', team_member='__None').status_code, 302)
        after = self.snapshot()
        for original in unaffected:
            self.assertIn(original, after)
        for member in (1, 2):
            self.assertIsNone(ScheduleEntry.query.filter_by(team_member_id=member, date=START).first())
            self.assertEqual(ScheduleEntry.query.filter_by(team_member_id=member, date=START + timedelta(days=5)).count(), 1)

    def test_individual_with_team_does_not_modify_peers(self):
        peer = self.entry(member=2)
        original_id = peer.id
        self.assertEqual(self.save(team='1', team_member='1').status_code, 302)
        self.assertEqual(db.session.get(ScheduleEntry, original_id).start_time, time(8))
        self.assertEqual(ScheduleEntry.query.filter_by(team_member_id=2).count(), 1)

    def test_foreign_retired_mismatched_and_empty_targets_are_rejected(self):
        self.entry()
        before = self.snapshot()
        for changes in [dict(team='2', team_member='__None'), dict(team_member='3'),
                        dict(team_member='4'), dict(team='3', team_member='1'),
                        dict(team='__None', team_member='__None')]:
            with self.subTest(changes=changes):
                self.assertEqual(self.save(**changes).status_code, 200)
                self.assertEqual(self.snapshot(), before)

    def test_empty_team_is_not_reported_as_success(self):
        db.session.add(Team(id=8, name='Empty', store_id=1))
        db.session.commit()
        response = self.save(team='8', team_member='__None')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No active technicians', response.data)
        self.assertEqual(ScheduleEntry.query.count(), 0)

    def test_permission_is_required_even_for_direct_post(self):
        self.login(2)
        self.assertEqual(self.save().status_code, 403)
        self.assertEqual(self.client.get('/generate_schedule').status_code, 403)
        self.assertEqual(ScheduleEntry.query.count(), 0)

    def test_form_only_lists_current_store_active_technicians(self):
        page = self.client.get('/generate_schedule')
        self.assertEqual(page.status_code, 200)
        self.assertNotIn(b'Foreign technician', page.data)
        self.assertNotIn(b'Retired', page.data)
        self.assertIn(b'Red technician', page.data)
        self.assertIn(b'Add missing days', page.data)
        self.assertIn(b'Replace work schedule', page.data)

    def test_replacement_requires_confirmation_and_valid_range_days_times(self):
        self.entry()
        before = self.snapshot()
        invalid = [dict(confirm_replace=''), dict(end_date='2026-11-08'),
                   dict(start_date='not-a-date'), dict(days_of_week=[]), dict(days_of_week=['7']),
                   dict(end_time='08:00'), dict(lunch_start='12:00'),
                   dict(lunch_start='07:00', lunch_end='08:00'),
                   dict(lunch_start='14:00', lunch_end='13:00'), dict(operation='unknown')]
        for changes in invalid:
            with self.subTest(changes=changes):
                response = self.save(**changes)
                self.assertEqual(response.status_code, 200)
                self.assertIn(b'The schedule was not saved', response.data)
                self.assertEqual(self.snapshot(), before)

    def test_monday_zero_is_valid_weekday_and_range_is_inclusive(self):
        response = self.save(days_of_week=['0'], end_date=START.isoformat())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ScheduleEntry.query.one().date, START)

    def test_holiday_converts_existing_work_and_new_holiday_is_untimed(self):
        holiday = date(2027, 1, 1)
        self.entry(day=holiday)
        self.assertEqual(self.save(start_date='2027-01-01', end_date='2027-01-01',
                                   days_of_week=['4']).status_code, 302)
        row = ScheduleEntry.query.one()
        self.assertEqual(row.schedule_type, 'HOLIDAY')
        self.assertIsNone(row.start_time)
        self.assertIsNone(row.lunch_start)
        self.assertEqual(row.notes, 'Shop Holiday')
        self.assertEqual(self.save(team_member='2', start_date='2027-01-01',
                                   end_date='2027-01-01', days_of_week=['4']).status_code, 302)
        self.assertEqual(ScheduleEntry.query.filter_by(schedule_type='HOLIDAY').count(), 2)

    def test_existing_duplicate_days_block_replace_without_partial_writes(self):
        self.entry()
        self.entry(day=START + timedelta(days=1))
        self.entry(day=START + timedelta(days=1), kind='PTO')
        before = self.snapshot()
        response = self.save()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Multiple entries exist', response.data)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.save(operation='add').status_code, 302)

    def test_database_error_rolls_back_deletes_updates_and_inserts(self):
        self.entry()
        self.entry(day=START + timedelta(days=1))
        before = self.snapshot()
        with patch.object(db.session, 'commit', side_effect=SQLAlchemyError('simulated commit failure')):
            response = self.save()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No changes were applied', response.data)
        self.assertEqual(self.snapshot(), before)

    def test_database_error_after_flush_rolls_back_all_changes(self):
        self.entry()
        self.entry(day=START + timedelta(days=1))
        before = self.snapshot()

        def flush_then_fail():
            db.session.flush()  # Exercise real UPDATE, DELETE and INSERT statements.
            raise SQLAlchemyError('simulated failure after SQL execution')

        with patch.object(db.session, 'commit', side_effect=flush_then_fail):
            response = self.save()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No changes were applied', response.data)
        self.assertEqual(self.snapshot(), before)

    def test_get_result_ids_cannot_leak_other_store_schedules(self):
        self.entry(member=3, notes='Foreign secret fixture')
        response = self.client.get('/generate_schedule?start=2026-11-09&end=2026-11-15&member=3')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'Foreign secret fixture', response.data)
        for args in ['start=bad&end=2026-11-15&member=1',
                     'start=2026-11-15&end=2026-11-09&member=1']:
            self.assertEqual(self.client.get('/generate_schedule?' + args).status_code, 200)

    def test_csrf_protection_rejects_missing_token(self):
        self.app.config['WTF_CSRF_ENABLED'] = True
        self.assertEqual(self.save().status_code, 200)
        self.assertEqual(ScheduleEntry.query.count(), 0)

    def test_postgresql_lock_is_scoped_to_technician_table(self):
        query = TeamMember.query.join(Team).filter(
            Team.store_id == 1, TeamMember.retired_at.is_(None), TeamMember.team_id == 1,
        ).order_by(TeamMember.id).with_for_update(of=TeamMember)
        sql = str(query.statement.compile(dialect=postgresql.dialect()))
        self.assertIn('FOR UPDATE OF team_member', sql)
        self.assertIn('team.store_id =', sql)


class SchedulePlanTests(unittest.TestCase):
    def test_last_representable_date_does_not_overflow(self):
        plan = plan_recurring_schedule(
            [1], [], date.max, date.max, [date.max.weekday()], set(), SHIFT, replace=True,
        )
        self.assertEqual(len(plan.creates), 1)
        self.assertEqual(plan.creates[0]['date'], date.max)

    def test_unknown_and_null_types_are_protected_without_mutation(self):
        for kind in [None, 'CUSTOM', 'PTO']:
            row = SimpleNamespace(team_member_id=1, date=START, schedule_type=kind, **SHIFT)
            plan = plan_recurring_schedule([1], [row], START, END, [0, 1], set(), SHIFT, replace=True)
            self.assertEqual(plan.protected, 1)
            self.assertEqual(plan.updates, [])
            self.assertEqual(plan.deletes, [])
            self.assertEqual(row.schedule_type, kind)

    def test_planner_refuses_out_of_scope_rows_and_invalid_ranges(self):
        row = SimpleNamespace(team_member_id=2, date=START, schedule_type='WORK', **SHIFT)
        for args in [([1], [row], START, END, [0]), ([1], [], END, START, [0]),
                     ([1], [], START, END, []), ([1], [], START, END, [7])]:
            with self.assertRaises(ValueError):
                plan_recurring_schedule(*args, set(), SHIFT, replace=True)


if __name__ == '__main__':
    unittest.main()
