"""Store production progress and local technician development."""
import sqlite3
from datetime import date, datetime, timedelta
from pytz import timezone
from flask import Blueprint, abort, current_app, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from wtforms import DateField, IntegerField, SelectField, StringField
from wtforms.validators import DataRequired, InputRequired, Length, NumberRange
from blueprints.management_intelligence import pilot_access
from extensions import db
from models import ASM, RepairOrder, Team, TeamMember, ScheduleEntry, WorkLog
from services.local_focus import snapshot_key
from services.technician_development import active_technicians, development_records, job_depth, responsibility_coverage
from services.work_distribution import booked_hour_shares
from utils.permissions import has_capability, require_capability

team_performance_bp = Blueprint('team_performance', __name__)


class CoverageFollowUpForm(FlaskForm):
    technician_id = IntegerField(validators=[InputRequired()])


class CriticalJobForm(FlaskForm):
    name = StringField("Critical job", filters=[lambda value: " ".join((value or "").split())],
                       validators=[DataRequired(), Length(max=100)])
    coverage_target = IntegerField("Independent techs needed", validators=[InputRequired(), NumberRange(min=1, max=1000)])


class SkillCheckForm(FlaskForm):
    technician = SelectField("Technician", coerce=int)
    status = SelectField("What did you verify?", choices=[
        ("learning", "Learning with a lead tech"), ("independent", "Can do it independently"),
        ("needs_training", "Needs training"),
    ])
    observed_on = DateField("Date checked", validators=[InputRequired()])
    evidence = StringField("RO, sign-off, or training record", filters=[lambda value: (value or "").strip()],
                           validators=[DataRequired(), Length(max=300)])


class JobFollowUpForm(FlaskForm):
    pass


class ResponsibilityForm(FlaskForm):
    name = StringField("Critical responsibility", filters=[lambda value: " ".join((value or "").split())],
                       validators=[DataRequired(), Length(max=100)])
    primary_person = StringField("Person who normally handles it", filters=[lambda value: " ".join((value or "").split())],
                                 validators=[DataRequired(), Length(max=100)])


class BackupCheckForm(FlaskForm):
    person = StringField("Backup person", filters=[lambda value: " ".join((value or "").split())],
                         validators=[DataRequired(), Length(max=100)])
    status = SelectField("Coverage status", choices=[
        ("verified", "Demonstrated independent coverage"), ("unconfirmed", "Coverage unconfirmed"),
    ])
    observed_on = DateField("Date checked", validators=[InputRequired()])
    evidence = StringField("Handoff, drill, or sign-off reference", filters=[lambda value: (value or "").strip()],
                           validators=[DataRequired(), Length(max=300)])


@team_performance_bp.route("/technician-development", methods=["GET", "POST"])
@login_required
@require_capability("manage.view")
def technician_development():
    pilot, database = pilot_access()
    store_id = pilot["store_id"]
    today = datetime.now(timezone("America/Los_Angeles")).date()
    roster = active_technicians(store_id, today)
    job_form = CriticalJobForm(prefix="job", coverage_target=2)
    skill_form = SkillCheckForm(prefix="skill", observed_on=today)
    skill_form.technician.choices = list(roster.items())
    follow_form = JobFollowUpForm(prefix="follow")
    selected_job = request.args.get("job", type=int)
    with development_records(database) as connection:
        jobs = job_depth(connection, store_id, roster)
        job = jobs.get(selected_job)
        if selected_job is not None and job is None:
            abort(404)
        if request.method == "POST":
            operation = request.form.get("operation")
            if operation == "add":
                if job_form.validate_on_submit():
                    try:
                        added = connection.execute(
                            "INSERT INTO critical_jobs (store_id, name, coverage_target) VALUES (?, ?, ?)",
                            (store_id, job_form.name.data, job_form.coverage_target.data),
                        )
                    except sqlite3.IntegrityError:
                        job_form.name.errors.append("That job is already on the list.")
                    else:
                        return redirect(url_for(".technician_development", job=added.lastrowid))
            elif operation == "record" and job:
                if skill_form.validate_on_submit():
                    if skill_form.observed_on.data > today:
                        skill_form.observed_on.errors.append("Enter today or an earlier date.")
                    else:
                        connection.execute("""
                            INSERT INTO skill_checks (job_id, technician_id, status, observed_on, evidence, entered_by)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (job["id"], skill_form.technician.data, skill_form.status.data,
                              skill_form.observed_on.data.isoformat(), skill_form.evidence.data, current_user.username))
                        return redirect(url_for(".technician_development", job=selected_job))
            elif operation == "follow" and job:
                if not follow_form.validate_on_submit():
                    abort(400)
                scenario = dict(
                    job=job["name"], job_id=job["id"], through=today.isoformat(), learning=len(job["learning"]),
                    independent=len(job["independent"]), unknown=job["unknown"], target=job["coverage_target"],
                    evidence_key=snapshot_key([row["id"] for status in ("learning", "independent", "needs_training")
                                               for row in job[status]]),
                    action=f"Choose a learner and lead tech for {job['name']}. Set up supervised work and an independent check.",
                    expected=f"Verify {job['coverage_target']} active techs can complete {job['name']} independently. "
                             "Record the RO or sign-off and any coverage still missing.",
                )
                if not job["gap"]:
                    scenario["action"] = f"Check backup availability for {job['name']} against the upcoming schedule."
                    scenario["expected"] = "Confirm who can cover the job and record any uncovered shifts."
                draft = snapshot_key(scenario)
                session["tsi_development_draft"] = dict(
                    key=draft, store_id=store_id, user_id=current_user.get_id(), scenario=scenario,
                )
                return redirect(url_for("management_intelligence.overview", calculator="tsi_development", plan=draft))
            else:
                abort(400)
    return render_template("technician_development.html", title="Technician Sustainability Index (TSI)",
                           jobs=jobs.values(), job=job, roster=roster, job_form=job_form,
                           skill_form=skill_form, follow_form=follow_form)


@team_performance_bp.route("/structural-concentration", methods=["GET", "POST"])
@login_required
@require_capability("manage.view")
def structural_concentration():
    pilot, database = pilot_access()
    store_id = pilot["store_id"]
    today = datetime.now(timezone("America/Los_Angeles")).date()
    roster = active_technicians(store_id, today)
    responsibility_form = ResponsibilityForm(prefix="responsibility")
    backup_form = BackupCheckForm(prefix="backup", observed_on=today)
    follow_form = JobFollowUpForm(prefix="follow")
    kind = request.args.get("kind")
    entry_id = request.args.get("entry", type=int)
    with development_records(database) as connection:
        jobs = job_depth(connection, store_id, roster)
        responsibilities = responsibility_coverage(connection, store_id)
        selected = {"job": jobs, "responsibility": responsibilities}.get(kind, {}).get(entry_id)
        if kind and selected is None:
            abort(404)
        if request.method == "POST":
            operation = request.form.get("operation")
            if operation == "add":
                if responsibility_form.validate_on_submit():
                    try:
                        added = connection.execute("""
                            INSERT INTO critical_responsibilities (store_id, name, primary_person) VALUES (?, ?, ?)
                        """, (store_id, responsibility_form.name.data, responsibility_form.primary_person.data))
                    except sqlite3.IntegrityError:
                        responsibility_form.name.errors.append("That responsibility is already on the list.")
                    else:
                        return redirect(url_for(".structural_concentration", kind="responsibility", entry=added.lastrowid))
            elif operation == "record" and kind == "responsibility":
                if backup_form.validate_on_submit():
                    if backup_form.observed_on.data > today:
                        backup_form.observed_on.errors.append("Enter today or an earlier date.")
                    elif backup_form.person.data.casefold() == selected["primary_person"].casefold():
                        backup_form.person.errors.append("Choose someone other than the primary person.")
                    else:
                        connection.execute("""
                            INSERT INTO backup_checks (responsibility_id, person, status, observed_on, evidence, entered_by)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (entry_id, backup_form.person.data, backup_form.status.data,
                              backup_form.observed_on.data.isoformat(), backup_form.evidence.data, current_user.username))
                        return redirect(url_for(".structural_concentration", kind=kind, entry=entry_id))
            elif operation == "follow" and selected:
                if not follow_form.validate_on_submit():
                    abort(400)
                checks = selected["independent"] if kind == "job" else selected["backups"]
                primary = (checks[0]["technician"] if len(checks) == 1 else None) if kind == "job" else selected["primary_person"]
                coverage_count = len(checks)
                scenario = dict(
                    kind=kind, entry_id=entry_id, subject=selected["name"], through=today.isoformat(),
                    primary=primary, coverage_count=coverage_count, evidence_key=snapshot_key([row["id"] for row in checks]),
                    action=f"Run an absence handoff for {selected['name']}. Have a second person complete the work "
                           "and check access, instructions, and shift coverage.",
                    expected=f"Name the person who covered {selected['name']} and record the completed handoff, "
                             "evidence, and any gaps still open.",
                )
                draft = snapshot_key(scenario)
                session["sci_coverage_draft"] = dict(
                    key=draft, store_id=store_id, user_id=current_user.get_id(), scenario=scenario,
                )
                return redirect(url_for("management_intelligence.overview", calculator="sci_coverage", plan=draft))
            else:
                abort(400)
    return render_template("structural_concentration.html", title="Structural Concentration Indicator (SCI)",
                           jobs=sorted(jobs.values(), key=lambda job: (len(job["independent"]) != 1, bool(job["independent"]), job["name"].casefold())),
                           responsibilities=sorted(responsibilities.values(), key=lambda item: bool(item["backups"])),
                           selected=selected, kind=kind, responsibility_form=responsibility_form,
                           backup_form=backup_form, follow_form=follow_form)


def progress(actual, target):
    return dict(actual=actual, target=target, gap=actual-target,
                remaining=max(target-actual, 0),
                percent=actual / target * 100 if target > 0 else None)


def summarize_progress(rows, period):
    hours = [row[period] for row in rows]
    return dict(
        progress(sum(row["actual"] for row in hours), sum(row["target"] for row in hours)),
        bookings=sum(row["bookings"] for row in hours),
        bookings_without_target=sum(row["bookings"] for row in hours if row["target"] <= 0),
        scheduled_without_target=any(row["workdays"] and row["target"] <= 0 for row in hours),
    )


def build_progress(members, schedules, logs, today):
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    periods = [('today', today), ('week', week_start), ('month', month_start)]
    rows = []
    for member in members:
        dpo = float((member.calculated_dpo if member.dpo_calculation_mode == 'calculated'
                     else member.daily_production_objective) or 0)
        # A technician has one daily objective even if multiple shifts are entered.
        retired_at = getattr(member, "retired_at", None)
        workdays = {s.date for s in schedules if s.team_member_id == member.id
                    and s.schedule_type == 'WORK' and s.date <= today
                    and (not retired_at or s.date < retired_at.date())}
        bookings = [log for log in logs if log.team_member_id == member.id]
        if retired_at and retired_at.date() <= today and not bookings and not workdays:
            continue
        row = dict(id=member.id, name=member.name, team=member.team.name, dpo=dpo,
                   scheduled=today in workdays)
        for key, start in periods:
            target = sum(dpo for day in workdays if start <= day <= today)
            period_logs = [log for log in bookings if start <= log.date <= today]
            actual = sum(float(log.flat_rate_hours or 0) for log in period_logs)
            row[key] = dict(progress(actual, target), bookings=len(period_logs), workdays=sum(
                start <= day <= today for day in workdays
            ))
        rows.append(row)
    totals = {key: summarize_progress(rows, key) for key, _ in periods}
    return rows, totals


@team_performance_bp.route('/team_performance', methods=['GET', 'POST'])
@login_required
@require_capability('routesheet.view')
def team_performance():
    store_id = current_user.store_id
    if not store_id:
        abort(403)
    now = datetime.now(timezone('America/Los_Angeles'))
    pilot = current_app.config.get("MI_LOCAL_PILOT")
    if pilot and pilot["store_id"] != store_id:
        pilot = None
    try:
        report_date = request.args.get("date")
        today = date.fromisoformat(report_date) if report_date else (
            pilot["period_end"] if pilot else now.date()
        )
        if not date(2, 1, 1) <= today <= now.date():
            abort(400)
    except ValueError:
        abort(400)
    period = request.args.get("period", "month")
    starts = {
        "today": today, "week": today - timedelta(days=today.weekday()), "month": today.replace(day=1)
    }
    if period not in starts:
        abort(400)
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
    total = totals[period]
    rows.sort(key=lambda row: (-row[period]["actual"], row["name"].casefold()))
    shares = booked_hour_shares(row[period]["actual"] for row in rows)
    show_shares = bool(shares) and shares[0] is not None
    for row, share in zip(rows, shares):
        row["share"] = share
    producers = [row for row in rows if row[period]["actual"] > 0]
    distribution = pilot and show_shares and not selected["tech_id"] and len(rows) >= 2
    leaders = producers[:2] if distribution else []
    if distribution:
        open_orders = RepairOrder.query.filter(
            RepairOrder.store_id == store_id,
            RepairOrder.team_member_id.in_([row["id"] for row in producers]),
            db.func.upper(db.func.trim(db.func.coalesce(RepairOrder.status, ""))) != "CLOSED",
        ).order_by(RepairOrder.promised_time.is_(None), RepairOrder.promised_time, RepairOrder.ro_number)
        orders_by_tech = {row["id"]: [] for row in producers}
        for order in open_orders:
            orders_by_tech[order.team_member_id].append(order)
        for row in producers:
            row["coverage_orders"] = orders_by_tech[row["id"]]
    coverage_form = CoverageFollowUpForm() if distribution and has_capability("manage.view") else None
    if request.method == "POST":
        if coverage_form is None:
            abort(403)
        if not coverage_form.validate_on_submit():
            abort(400)
        tech = next((row for row in producers if row["id"] == coverage_form.technician_id.data), None)
        if tech is None:
            abort(404)
        hours = tech[period]["actual"]
        scenario = dict(
            through=today.isoformat(), start=starts[period].isoformat(),
            technician_id=tech["id"], technician=tech["name"], team=tech["team"],
            hours=hours, share=tech["share"], total_hours=total["actual"], filters=selected,
            open_orders=len(tech["coverage_orders"]),
            order_fingerprint=snapshot_key([
                (order.ro_number, order.status, order.promised_time.isoformat() if order.promised_time else None)
                for order in tech["coverage_orders"]
            ]),
            action=f"Review upcoming work assigned to {tech['name']}. Name a qualified backup for each "
                   "job that needs coverage and check available time against customer promises.",
            expected="Record which ROs and hours the backup can cover, what is still uncovered, "
                     "and which promises were kept at the next coverage check.",
        )
        draft = snapshot_key(scenario)
        session["uvi_coverage_draft"] = dict(
            key=draft, store_id=store_id, user_id=current_user.get_id(), scenario=scenario,
        )
        return redirect(url_for("management_intelligence.overview", calculator="uvi_coverage", plan=draft))
    missing_schedule = sum(row[period]["workdays"] == 0 for row in rows if row[period]["bookings"])
    return render_template('team_performance.html', title='Team Performance', teams=teams, asms=asms,
                           members=members, selected=selected, rows=rows, totals=totals,
                           today=today, period=period, period_start=starts[period], total=total,
                           latest_date=now.date(), show_shares=show_shares, pilot=pilot,
                           missing_schedule=missing_schedule, leaders=leaders, distribution=distribution,
                           coverage_form=coverage_form)
