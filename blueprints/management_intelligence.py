"""Read-only Management Intelligence view for an explicitly configured SQLite pilot."""

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from flask import Blueprint, abort, current_app, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from pytz import timezone
from wtforms import DateField, HiddenField, SelectField, StringField, TextAreaField
from wtforms.validators import InputRequired, Length, Optional

from extensions import db
from mi_v5.vertical_slice import evaluate_case, load_store_period
from models import Team, TeamMember, WorkLog
from services.calculator_direction import CHECKS, calculator_direction
from services.local_focus import action_rows, action_status, focus_records, snapshot_key
from services.technician_development import active_technicians, development_records, job_depth, responsibility_coverage
from services.work_distribution import booked_hour_shares
from utils.permissions import has_capability, require_capability


management_intelligence_bp = Blueprint("management_intelligence", __name__)
DURABILITY_SOURCES = {"uvi_coverage", "tsi_development", "sci_coverage"}


class DecisionForm(FlaskForm):
    snapshot = HiddenField(validators=[InputRequired(), Length(max=64)])
    disposition = SelectField("Your decision", choices=[
        ("", "Choose a decision"), ("accept", "Accept"), ("modify", "Change it"),
        ("reject", "Decline"), ("defer", "Defer"),
    ], validators=[InputRequired()])
    rationale = TextAreaField("Why did you make this call?", validators=[InputRequired(), Length(max=2000)])
    owner = StringField("Who owns it?", validators=[Optional(), Length(max=120)])
    due_date = DateField("Due date", validators=[Optional()])
    action = TextAreaField("What should they do?", validators=[Optional(), Length(max=2000)])
    expected_result = TextAreaField("What would show it worked?", validators=[Optional(), Length(max=2000)])


class ReviewForm(FlaskForm):
    completed = SelectField("Was the work done?", choices=[
        ("", "Choose an update"), ("open", "Still open"), ("done", "Completed"),
    ], validators=[InputRequired()])
    outcome = SelectField("Did it work?", choices=[
        ("pending", "Not ready to judge"), ("worked", "Yes"),
        ("partial", "Partly"), ("missed", "No"),
    ], validators=[InputRequired()])
    observed = TextAreaField("What did you see?", validators=[InputRequired(), Length(max=2000)])
    evidence_reference = StringField("Where can we check it?", validators=[InputRequired(), Length(max=500)])
    observed_on = DateField("Date checked", validators=[InputRequired()])


def pilot_access():
    pilot = current_app.config.get("MI_LOCAL_PILOT")
    database = db.engine.url
    if not pilot or database.get_backend_name() != "sqlite" or not database.database:
        abort(404)
    if current_user.is_operator or current_user.store_id != pilot["store_id"]:
        abort(403)
    return pilot, database.database


def manager_focus(case, result):
    if not case.scheduled_operating_dates and result["true_potential"]["supported_demand_frh"] is None:
        return dict(
            priority="Check the schedule and available work",
            reason="We have booked hours, but we’re missing the tech schedule and a reliable count of the work available. We can’t tell what the shop could have produced.",
            action="Confirm who was scheduled and how much work was ready for the shop before changing the production target.",
        )
    return dict(
        priority=result["condition"]["title"],
        reason=result["management_position"]["why_it_matters"],
        action=result["management_position"]["recommended_intervention"],
    )


def technician_id_review(pilot):
    if not pilot or pilot["store_id"] != current_user.store_id:
        return None
    rows = current_app.config.get("WORK_LOG_SOURCE_REVIEW", [])
    if not rows:
        return None
    return dict(rows=rows, bookings=sum(row["count"] for row in rows),
                sold_hours=pilot["unmapped_sold_hours"])


@management_intelligence_bp.route("/management-intelligence", methods=["GET", "POST"])
@login_required
@require_capability("manage.view")
def overview():
    pilot, database = pilot_access()

    case, result = evaluate_pilot(pilot)
    focus = manager_focus(case, result)
    calculator = request.args.get("calculator")
    if calculator not in CHECKS:
        calculator = None
    if calculator:
        guidance = calculator_direction(calculator, case, result)
        focus = dict(priority=CHECKS[calculator]["label"], reason=focus["reason"], action=guidance["direction"])
    snapshot = dict(result=result, focus=focus, source=pilot.get("dataset_id"),
                    start=pilot["period_start"].isoformat(), end=pilot["period_end"].isoformat())
    if calculator:
        snapshot["calculator"] = calculator
    scenario = None
    draft_key = request.args.get("plan")
    scenario_name = {
        "pace_recovery_calculator": "pace_recovery",
        "appointment_lift_calculator": "appointment_lift",
        "uvi_coverage": "uvi_coverage",
        "tsi_development": "tsi_development",
        "sci_coverage": "sci_coverage",
    }.get(calculator)
    if scenario_name and draft_key:
        draft = session.get(f"{scenario_name}_draft", {})
        if (draft.get("key") != draft_key or draft.get("store_id") != pilot["store_id"]
                or draft.get("user_id") != current_user.get_id()):
            abort(404, description="Open the source page and draft the follow-up again.")
        scenario = draft["scenario"]
        snapshot[scenario_name] = scenario
        if scenario_name == "sci_coverage":
            focus.update(
                reason=f"Check who can cover {scenario['subject']} when the usual person is out.",
                action=scenario["action"],
            )
    fingerprint = snapshot_key(snapshot)
    form = DecisionForm(
        snapshot=fingerprint, action=scenario["action"] if scenario else None,
        expected_result=scenario["expected"] if scenario else None,
    )
    error = None
    with focus_records(database) as connection:
        if form.validate_on_submit():
            actionable = form.disposition.data in ("accept", "modify")
            owner, action, expected = [field.data.strip() if field.data else None for field in
                                       (form.owner, form.action, form.expected_result)]
            if form.snapshot.data != fingerprint:
                error = "The evidence changed. Reload and review the latest recommendation before saving."
            elif not form.rationale.data.strip():
                error = "Enter why you made this call."
            elif actionable and not (owner and form.due_date.data and action and expected):
                error = "Enter an owner, due date, action and expected result."
            else:
                try:
                    saved = connection.execute("""
                        INSERT INTO focus_decisions (store_id, snapshot_key, snapshot, entered_by, disposition,
                            rationale, owner, due_date, action, expected_result)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (pilot["store_id"], fingerprint, json.dumps(snapshot), current_user.username,
                          form.disposition.data, form.rationale.data.strip(),
                          owner if actionable else None, form.due_date.data.isoformat() if actionable else None,
                          action if actionable else None, expected if actionable else None))
                except sqlite3.IntegrityError:
                    error = "A decision has already been recorded for this recommendation."
                else:
                    return redirect(url_for(".follow_up", decision_id=saved.lastrowid))
        decisions = action_rows(connection, pilot["store_id"], datetime.now(timezone("America/Los_Angeles")).date())
    return render_template(
        "local_management_intelligence.html",
        title="Action & Follow-Up",
        pilot=pilot,
        result=result,
        focus=focus,
        calculator=calculator,
        scenario=scenario,
        checks=CHECKS,
        tech_id_review=technician_id_review(pilot),
        form=form,
        error=error,
        decisions=decisions,
        current_decision=next((row for row in decisions if row["snapshot_key"] == fingerprint), None),
        schedules_present=bool(case.scheduled_operating_dates),
    )


@management_intelligence_bp.get("/management-intelligence/recap")
@login_required
def recap():
    if not (has_capability("manage.view") or has_capability("mi.recap.view")):
        abort(403)
    pilot, database = pilot_access()
    durability_only = request.args.get("scope") == "durability"
    with focus_records(database) as connection:
        actions = [
            row for row in action_rows(connection, pilot["store_id"], datetime.now(timezone("America/Los_Angeles")).date())
            if row["action"] and (not durability_only or row["calculator"] in DURABILITY_SOURCES)
        ]
    return render_template(
        "local_mi_recap.html", title="Management Recap", pilot=pilot, actions=actions, checks=CHECKS,
        can_follow_up=has_capability("manage.view"), durability_only=durability_only,
    )


@management_intelligence_bp.get("/management-intelligence/structural-performance")
@login_required
@require_capability("manage.view")
def structural_performance():
    pilot, database = pilot_access()
    store_id = pilot["store_id"]
    today = datetime.now(timezone("America/Los_Angeles")).date()
    period_end = pilot["period_end"]
    evidence_start = max(period_end.replace(day=1), pilot["period_start"])
    booked_hours = db.func.sum(WorkLog.flat_rate_hours)
    booked = (
        db.session.query(TeamMember.name, booked_hours.label("hours"))
        .join(WorkLog, WorkLog.team_member_id == TeamMember.id)
        .join(Team, TeamMember.team_id == Team.id)
        .filter(Team.store_id == store_id, WorkLog.date.between(evidence_start, period_end))
        .group_by(TeamMember.id, TeamMember.name)
        .order_by(booked_hours.desc(), db.func.lower(TeamMember.name))
        .all()
    )
    shares = booked_hour_shares(row.hours for row in booked)
    leaders = [
        dict(name=row.name, hours=row.hours, share=share)
        for row, share in zip(booked[:2], shares[:2]) if share is not None and row.hours > 0
    ]
    roster = active_technicians(store_id, today)
    with development_records(database) as connection:
        jobs = list(job_depth(connection, store_id, roster).values())
        responsibilities = list(responsibility_coverage(connection, store_id).values())
    with focus_records(database) as connection:
        actions = [row for row in action_rows(connection, store_id, today)
                   if row["action"] and row["calculator"] in DURABILITY_SOURCES]
    reviewed = [row for row in actions if row["stage"] == "reviewed"]
    reviewed.sort(key=lambda row: (row["observed_on"], row["id"]), reverse=True)
    return render_template(
        "structural_performance.html", title="Structural Performance Index (SPI)", pilot=pilot,
        evidence_start=evidence_start, today=today, leaders=leaders,
        jobs=jobs, responsibilities=responsibilities, reviewed=reviewed[:3],
        outcome_counts={outcome: sum(row["latest_outcome"] == outcome for row in reviewed)
                        for outcome in ("worked", "partial", "missed")},
        pending=len(actions) - len(reviewed), checks=CHECKS,
    )


@management_intelligence_bp.route("/management-intelligence/decisions/<int:decision_id>", methods=["GET", "POST"])
@login_required
@require_capability("manage.view")
def follow_up(decision_id):
    pilot, database = pilot_access()
    form = ReviewForm()
    error = None
    with focus_records(database) as connection:
        decision = connection.execute(
            "SELECT * FROM focus_decisions WHERE id = ? AND store_id = ?", (decision_id, pilot["store_id"]),
        ).fetchone()
        if decision is None:
            abort(404)
        if form.validate_on_submit():
            if not decision["action"]:
                abort(400)
            if form.completed.data != "done" and form.outcome.data != "pending":
                error = "Record the work as completed before judging the result."
            elif not form.observed.data.strip() or not form.evidence_reference.data.strip():
                error = "Describe what you saw and where it can be checked."
            else:
                connection.execute("""
                    INSERT INTO focus_reviews (decision_id, entered_by, completed, outcome, observed,
                        evidence_reference, observed_on) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (decision_id, current_user.username, form.completed.data, form.outcome.data,
                      form.observed.data.strip(), form.evidence_reference.data.strip(), form.observed_on.data.isoformat()))
                return redirect(url_for(".follow_up", decision_id=decision_id))
        reviews = connection.execute(
            "SELECT * FROM focus_reviews WHERE decision_id = ? ORDER BY id DESC", (decision_id,),
        ).fetchall()
    latest = reviews[0] if reviews else None
    today = datetime.now(timezone("America/Los_Angeles")).date()
    stage, work_status, result_status = action_status(
        decision["due_date"], latest["completed"] if latest else None,
        latest["outcome"] if latest else None, today,
    )
    return render_template(
        "local_focus_follow_up.html", title="Action & Follow-Up", decision=decision,
        snapshot=json.loads(decision["snapshot"]), reviews=reviews, latest=latest,
        form=form, error=error, stage=stage, work_status=work_status, result_status=result_status,
    )


def evaluate_pilot(pilot):
    database = db.engine.url
    case = load_store_period(
        Path(database.database),
        legacy_store_id=pilot["store_id"],
        period_start=pilot["period_start"],
        period_end=pilot["period_end"],
    )
    return case, evaluate_case(case).to_dict()
