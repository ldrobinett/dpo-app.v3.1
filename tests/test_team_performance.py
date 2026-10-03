import unittest
from datetime import date
from types import SimpleNamespace as Obj
from flask import Flask, g
from flask_login import LoginManager
from extensions import db
from models import ManagedStore, Team, TeamMember, ASM, User, Role, Capability, ScheduleEntry, WorkLog
from blueprints.team_performance import team_performance_bp, build_progress

class PerformanceTests(unittest.TestCase):
    def test_cross_month_and_schedule_rules(self):
        tech=Obj(id=1,name='Tech',team=Obj(name='A'),dpo_calculation_mode='calculated',calculated_dpo=10,daily_production_objective=8)
        schedules=[Obj(team_member_id=1,date=date(2026,9,30),schedule_type='WORK'),Obj(team_member_id=1,date=date(2026,10,1),schedule_type='WORK'),Obj(team_member_id=1,date=date(2026,10,1),schedule_type='WORK'),Obj(team_member_id=1,date=date(2026,10,2),schedule_type='VACATION')]
        logs=[Obj(team_member_id=1,date=date(2026,9,30),flat_rate_hours=9),Obj(team_member_id=1,date=date(2026,10,1),flat_rate_hours=12)]
        rows, totals=build_progress([tech],schedules,logs,date(2026,10,2))
        self.assertEqual(totals['week']['target'],20)
        self.assertEqual(totals['week']['actual'],21)
        self.assertEqual(totals['month']['target'],10)
        self.assertEqual(rows[0]['today']['percent'],None)
        self.assertEqual(rows[0]['today']['remaining'],0)

    def test_store_filters_and_access(self):
        app=Flask(__name__);app.config.update(SECRET_KEY='test',SQLALCHEMY_DATABASE_URI='sqlite://',TESTING=True)
        db.init_app(app);login=LoginManager(app)
        @login.user_loader
        def load(uid):return db.session.get(User,int(uid))
        @app.before_request
        def fresh_request_user():g.pop("_login_user", None)
        app.register_blueprint(team_performance_bp)
        # Use real template with a minimal base, to exercise formatting and filtering.
        from jinja2 import ChoiceLoader, FileSystemLoader, DictLoader
        app.jinja_loader=ChoiceLoader([DictLoader({'base.html':'{% block content %}{% endblock %}'}),FileSystemLoader('templates')])
        with app.app_context():
            db.create_all()
            stores=[ManagedStore(name=n,url='test',admin_username='test') for n in ['Local','Other']];db.session.add_all(stores);db.session.flush()
            teams=[Team(name=n,store_id=s.id) for n,s in zip(['Local team','Foreign team'],stores)];db.session.add_all(teams);db.session.flush()
            techs=[TeamMember(name=n,team_id=t.id,daily_production_objective=10) for n,t in zip(['Local tech','Foreign tech'],teams)];db.session.add_all(techs)
            cap=Capability(key='routesheet.view');role=Role(name='Advisor',store_id=stores[0].id,capabilities=[cap]);user=User(username='test',password='unused',store_id=stores[0].id,roles=[role]);db.session.add(user)
            asm=ASM(name='Local ASM',store_id=stores[0].id,team_id=teams[0].id);db.session.add(asm);db.session.commit()
            client=app.test_client();self.assertEqual(client.get('/team_performance').status_code,401)
            with client.session_transaction() as session:session['_user_id']=str(user.id);session['_fresh']=True
            response=client.get('/team_performance');self.assertEqual(response.status_code,200);self.assertIn(b'Local tech',response.data);self.assertNotIn(b'Foreign tech',response.data)
            self.assertEqual(client.get('/team_performance?team_id='+str(teams[1].id)).status_code,404)
            self.assertEqual(client.get('/team_performance?team_id=bad').status_code,400)
            self.assertEqual(client.get('/team_performance?asm_id='+str(asm.id)+'&tech_id='+str(techs[0].id)).status_code,200)
            user.roles=[];db.session.commit();self.assertEqual(client.get('/team_performance').status_code,403)

if __name__=='__main__':unittest.main()
