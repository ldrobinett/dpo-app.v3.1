from functools import wraps
from datetime import datetime
import logging

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import login_user, logout_user, login_required, current_user

from extensions import db, bcrypt
from models import OperatorUser, ManagedStore, User, Role, Capability

operator_bp = Blueprint("operator", __name__, url_prefix="/operator")


def operator_required() -> bool:
    if not getattr(current_user, "is_authenticated", False):
        return False
    return getattr(current_user, "is_operator", False) is True


def operator_only(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not getattr(current_user, "is_authenticated", False):
            return redirect(url_for("operator.login"))
        if not operator_required():
            abort(403)
        return view_func(*args, **kwargs)
    return wrapped


def _get_store_or_404(store_id: int) -> ManagedStore:
    store = db.session.get(ManagedStore, store_id)
    if not store:
        abort(404)
    return store


def _operator_pw_ok(password: str) -> bool:
    return bool(password) and current_user.check_password(bcrypt, password)


@operator_bp.route("/login", methods=["GET", "POST"])
def login():
    if operator_required():
        return redirect(url_for("operator.store_index"))

    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""

        operator = OperatorUser.query.filter_by(username=username, is_active=True).first()
        if not operator or not operator.check_password(bcrypt, password):
            flash("Invalid operator credentials.", "danger")
            return redirect(url_for("operator.login"))

        login_user(operator, remember=False)
        return redirect(url_for("operator.store_index"))

    return render_template("operator/login.html", title="Operator Login")


@operator_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("operator.login"))


@operator_bp.route("/stores", methods=["GET"])
@login_required
@operator_only
def store_index():
    stores = (
        ManagedStore.query
        .filter(ManagedStore.status.in_(["active", "archived"]))
        .order_by(ManagedStore.environment.asc(), ManagedStore.name.asc())
        .all()
    )
    return render_template("operator/stores.html", title="Store Index", stores=stores)


@operator_bp.route("/stores/deleted", methods=["GET"])
@login_required
@operator_only
def store_deleted_index():
    stores = (
        ManagedStore.query
        .filter(ManagedStore.status == "deleted")
        .order_by(ManagedStore.environment.asc(), ManagedStore.name.asc())
        .all()
    )
    return render_template("operator/stores_deleted.html", title="Deleted Stores", stores=stores)


@operator_bp.route("/stores/new", methods=["GET", "POST"])
@login_required
@operator_only
def store_new():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        environment = (request.form.get("environment") or "prod").strip()
        status = (request.form.get("status") or "active").strip()
        url = (request.form.get("url") or "").strip()
        admin_username = (request.form.get("admin_username") or "").strip()
        admin_password = request.form.get("admin_password") or ""

        if not (name and url and admin_username and admin_password):
            flash("All fields are required.", "warning")
            return redirect(url_for("operator.store_new"))

        if status not in ("active", "archived"):
            status = "active"

        store = ManagedStore(
            name=name,
            environment=environment,
            status=status,
            url=url.rstrip("/"),
            admin_username=admin_username,
        )
        store.set_admin_password(admin_password)

        try:
            db.session.add(store)
            db.session.flush()

            admin_role = Role.query.filter_by(name="Admin", store_id=store.id).first()

            if not admin_role:
                capabilities = {cap.key: cap for cap in Capability.query.all()}
                admin_role_keys = [
                    "teams.manage",
                    "users.manage",
                    "routesheet.view",
                    "routesheet.edit",
                    "worklog.manage",
                    "finance.view",
                    "finance.edit",
                    "schedule.manage",
                    "routes.view",
                    "worklog.view",
                    "schedule.view",
                    "production.view",
                    "manage.view",
                    "calculators.view",
                    "onboarding.manage",
                ]

                admin_role = Role(name="Admin", store_id=store.id)
                admin_role.capabilities = [
                    capabilities[key] for key in admin_role_keys if key in capabilities
                ]
                db.session.add(admin_role)
                db.session.flush()

            admin_user = User(
                username=admin_username,
                password=bcrypt.generate_password_hash(admin_password).decode("utf-8"),
                store_id=store.id,
            )
            admin_user.roles.append(admin_role)
            db.session.add(admin_user)

            db.session.commit()
            flash("Store and admin user created.", "success")
            return redirect(url_for("operator.store_index"))

        except Exception:
            db.session.rollback()
            logging.exception("Failed to create store")
            flash("Failed to create store.", "danger")
            return redirect(url_for("operator.store_new"))

    return render_template("operator/store_form.html", title="Add Store", store=None)


@operator_bp.route("/stores/<int:store_id>/edit", methods=["GET", "POST"])
@login_required
@operator_only
def store_edit(store_id: int):
    store = _get_store_or_404(store_id)

    if request.method == "POST":
        store.name = (request.form.get("name") or "").strip()
        store.environment = (request.form.get("environment") or store.environment).strip()

        new_status = (request.form.get("status") or store.status).strip()
        if store.status != "deleted" and new_status in ("active", "archived"):
            store.status = new_status

        store.url = (request.form.get("url") or "").strip()
        store.admin_username = (request.form.get("admin_username") or "").strip()
        store.notes = (request.form.get("notes") or "").strip() or None

        new_password = request.form.get("admin_password") or ""
        if new_password.strip():
            store.set_admin_password(new_password)

        db.session.commit()
        flash("Store updated.", "success")
        return redirect(url_for("operator.store_index"))

    return render_template("operator/store_form.html", title="Edit Store", store=store)


@operator_bp.route("/stores/<int:store_id>/open", methods=["GET"])
@login_required
@operator_only
def open_store(store_id: int):
    store = _get_store_or_404(store_id)

    if store.status != "active":
        flash("Only active stores can be opened.", "warning")
        return redirect(url_for("operator.store_index"))

    logout_user()
    return redirect(store.url.rstrip("/") + "/login")


@operator_bp.route("/stores/<int:store_id>/archive", methods=["POST"])
@login_required
@operator_only
def store_archive(store_id: int):
    store = _get_store_or_404(store_id)

    if store.status == "deleted":
        flash("Cannot archive a deleted store.", "warning")
        return redirect(url_for("operator.store_index"))

    store.status = "archived"
    store.archived_at = datetime.utcnow()
    db.session.commit()

    flash("Store archived.", "warning")
    return redirect(url_for("operator.store_index"))


@operator_bp.route("/stores/<int:store_id>/restore", methods=["POST"])
@login_required
@operator_only
def store_restore(store_id: int):
    store = _get_store_or_404(store_id)

    store.status = "active"
    store.archived_at = None

    if hasattr(store, "deleted_at"):
        store.deleted_at = None

    db.session.commit()
    flash("Store restored.", "success")
    return redirect(request.referrer or url_for("operator.store_index"))


@operator_bp.route("/stores/<int:store_id>/delete", methods=["POST"])
@login_required
@operator_only
def store_soft_delete(store_id: int):
    store = _get_store_or_404(store_id)

    if store.status == "active":
        flash("Archive the store before deleting.", "warning")
        return redirect(url_for("operator.store_index"))

    store.status = "deleted"

    if hasattr(store, "deleted_at"):
        store.deleted_at = datetime.utcnow()

    db.session.commit()
    flash("Store soft-deleted (hidden).", "danger")
    return redirect(url_for("operator.store_index"))


@operator_bp.route("/stores/<int:store_id>/purge", methods=["POST"])
@login_required
@operator_only
def store_purge(store_id: int):
    store = _get_store_or_404(store_id)

    operator_password = request.form.get("operator_password") or ""
    confirm_phrase = (request.form.get("confirm_phrase") or "").strip()

    if not _operator_pw_ok(operator_password):
        flash("Operator password incorrect.", "danger")
        return redirect(request.referrer or url_for("operator.store_deleted_index"))

    if store.environment == "prod":
        flash("Purge is disabled for production stores.", "danger")
        return redirect(request.referrer or url_for("operator.store_deleted_index"))

    if store.status != "deleted":
        flash("Store must be soft-deleted before purge.", "warning")
        return redirect(request.referrer or url_for("operator.store_deleted_index"))

    if confirm_phrase != f"PURGE {store.id}":
        flash("Confirmation phrase mismatch (expected: PURGE <store_id>).", "danger")
        return redirect(request.referrer or url_for("operator.store_deleted_index"))

    try:
        User.query.filter(User.store_id == store.id).delete(synchronize_session=False)
        db.session.delete(store)
        db.session.commit()

        flash("Store fully purged (store + users).", "danger")
        return redirect(url_for("operator.store_index"))

    except Exception:
        db.session.rollback()
        logging.exception("Failed to purge store %s", store_id)
        flash("Purge failed. Nothing partially committed.", "danger")
        return redirect(request.referrer or url_for("operator.store_deleted_index"))


@operator_bp.route("/stores/<int:store_id>/reveal", methods=["POST"])
@login_required
@operator_only
def store_reveal(store_id: int):
    operator_password = request.form.get("operator_password") or ""
    if not _operator_pw_ok(operator_password):
        return jsonify({"error": "bad operator password"}), 401

    store = _get_store_or_404(store_id)

    if getattr(store, "status", None) == "deleted":
        return jsonify({"error": "store deleted"}), 400

    try:
        password = store.get_admin_password()
        return jsonify({"password": password})
    except Exception:
        return jsonify({"error": "decrypt failed"}), 500