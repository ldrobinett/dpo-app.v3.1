"""Store-scoped, read-only production progress for advisors and managers."""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from flask import Blueprint, abort, render_template, request
from flask_login import current_user, login_required
from models import ASM, Team, TeamMember, ScheduleEntry, WorkLog
from utils.permissions import require_capability

team_performance_bp = Blueprint('team_performance', __name__)


def progress(actual, target):
    return dict(actual=actual, target=target, gap=actual-target,
                remaining=max(target-actual, 0),
                percent=actual / target * 100 if target > 0 else None)


def build_progress(members, schedules, logs, today):
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    periods = [('today', today), ('week', week_start), ('month', month_start)]
    rows = []
    for member in members:
        dpo = float((member.calculated_dpo if member.dpo_calculation_mode == 'calculated'
                     else member.daily_production_objective) or 0)
        # A technician has one daily objective even if multiple shifts are entered.
        workdays = {s.date for s in schedules if s.team_member_id == member.id
                    and s.schedule_type == 'WORK' and s.date <= today}
        row = dict(id=member.id, name=member.name, team=member.team.name, dpo=dpo,
                   scheduled=today in workdays)
        for key, start in periods:
            target = sum(dpo for day in workdays if start <= day <= today)
            actual = sum(float(log.flat_rate_hours or 0) for log in logs
                         if log.team_member_id == member.id and start <= log.date <= today)
            row[key] = progress(actual, target)
        rows.append(row)
    totals = {key: progress(sum(row[key]['actual'] for row in rows),
                            sum(row[key]['target'] for row in rows)) for key, _ in periods}
    return rows, totals


@team_performance_bp.route('/team_performance')
@login_required
@require_capability('routesheet.view')
def team_performance():
    store_id = current_user.store_id
    if not store_id:
        abort(403)
    now = datetime.now(ZoneInfo('America/Los_Angeles'))
    today = now.date()
    earliest = min(today.replace(day=1), today-timedelta(days=today.weekday()))
    teams = Team.query.filter_by(store_id=store_id).order_by(Team.name).all()
    asms = ASM.query.filter_by(store_id=store_id).order_by(ASM.name).all()
    members = TeamMember.query.join(Team).filter(Team.store_id == store_id).order_by(Team.name, TeamMember.name).all()
    selected = {}
    for key, choices in [('team_id', teams), ('asm_id', asms), ('tech_id', members)]:
        raw = request.args.get(key, '')
        if not raw:
            selected[key] = None
        else:
            try:
                selected[key] = int(raw)
            except ValueError:
                abort(400)
            if selected[key] not in {item.id for item in choices}:
                abort(404)
    asm = next((a for a in asms if a.id == selected['asm_id']), None)
    filtered = [m for m in members
                if (not selected['team_id'] or m.team_id == selected['team_id'])
                and (not asm or m.team_id == asm.team_id)
                and (not selected['tech_id'] or m.id == selected['tech_id'])]
    ids = [m.id for m in filtered]
    schedules = ScheduleEntry.query.filter(ScheduleEntry.team_member_id.in_(ids), ScheduleEntry.date >= earliest, ScheduleEntry.date <= today).all() if ids else []
    logs = WorkLog.query.filter(WorkLog.team_member_id.in_(ids), WorkLog.date >= earliest, WorkLog.date <= today).all() if ids else []
    rows, totals = build_progress(filtered, schedules, logs, today)
    missing_schedule = [row['name'] for row in rows if not any(s.team_member_id == row['id'] and s.schedule_type == 'WORK' for s in schedules)]
    return render_template('team_performance.html', title='Team Performance', teams=teams, asms=asms,
                           members=members, selected=selected, rows=rows, totals=totals,
                           today=today, updated=now, missing_schedule=missing_schedule)
