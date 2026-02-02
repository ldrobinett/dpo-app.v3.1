from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db, bcrypt
from models import OperatorUser, ManagedStore

operator_bp = Blueprint("operator", __name__, url_prefix="/operator")


def operator_required():
    # Flask-Login uses is_authenticated; we also require operator identity
    if not getattr(current_user, "is_authenticated", False):
        return False
    return getattr(current_user, "is_operator", False) is True


@operator_bp.route("/login", methods=["GET", "POST"])
def login():
    if operator_required():
        return redirect(url_for("operator.store_index"))

    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""

        op = OperatorUser.query.filter_by(username=username, is_active=True).first()
        if not op or not op.check_password(bcrypt, password):
            flash("Invalid operator credentials.", "danger")
            return redirect(url_for("operator.login"))

        login_user(op, remember=False)
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
def store_index():
    if not operator_required():
        flash("Not authorized.", "danger")
        return redirect(url_for("main_bp.home") if "main_bp.home" else "/")

    stores = ManagedStore.query.order_by(ManagedStore.environment.asc(), ManagedStore.name.asc()).all()
    return render_template("operator/stores.html", title="Store Index", stores=stores)


@operator_bp.route("/stores/new", methods=["GET", "POST"])
@login_required
def store_new():
    if not operator_required():
        flash("Not authorized.", "danger")
        return redirect(url_for("operator.login"))

    if request.method == "POST":
        s = ManagedStore(
            name=(request.form.get("name") or "").strip(),
            environment=(request.form.get("environment") or "prod").strip(),
            status=(request.form.get("status") or "active").strip(),
            url=(request.form.get("url") or "").strip(),
            admin_username=(request.form.get("admin_username") or "").strip(),
            notes=(request.form.get("notes") or "").strip() or None,
        )
        admin_pw = request.form.get("admin_password") or ""
        if not (s.name and s.url and s.admin_username and admin_pw):
            flash("Name, URL, admin username, and admin password are required.", "warning")
            return redirect(url_for("operator.store_new"))

        s.set_admin_password(admin_pw)
        db.session.add(s)
        db.session.commit()
        flash("Store added.", "success")
        return redirect(url_for("operator.store_index"))

    return render_template("operator/store_form.html", title="Add Store", store=None)


@operator_bp.route("/stores/<int:store_id>/edit", methods=["GET", "POST"])
@login_required
def store_edit(store_id: int):
    if not operator_required():
        flash("Not authorized.", "danger")
        return redirect(url_for("operator.login"))

    s = db.session.get(ManagedStore, store_id)
    if not s:
        flash("Store not found.", "warning")
        return redirect(url_for("operator.store_index"))

    if request.method == "POST":
        s.name = (request.form.get("name") or "").strip()
        s.environment = (request.form.get("environment") or s.environment).strip()
        s.status = (request.form.get("status") or s.status).strip()
        s.url = (request.form.get("url") or "").strip()
        s.admin_username = (request.form.get("admin_username") or "").strip()
        s.notes = (request.form.get("notes") or "").strip() or None

        new_pw = request.form.get("admin_password") or ""
        if new_pw.strip():
            s.set_admin_password(new_pw)

        db.session.commit()
        flash("Store updated.", "success")
        return redirect(url_for("operator.store_index"))

    return render_template("operator/store_form.html", title="Edit Store", store=s)


@operator_bp.route("/stores/<int:store_id>/reveal", methods=["POST"])
@login_required
def store_reveal(store_id: int):
    """
    Reveal store admin password ONLY after re-confirming operator password.
    Returns JSON: {password: "..."}.
    """
    if not operator_required():
        return jsonify({"error": "not authorized"}), 403

    operator_password = request.form.get("operator_password") or ""
    if not current_user.check_password(bcrypt, operator_password):
        return jsonify({"error": "bad operator password"}), 401

    s = db.session.get(ManagedStore, store_id)
    if not s:
        return jsonify({"error": "not found"}), 404

    try:
        pw = s.get_admin_password()
        return jsonify({"password": pw})
    except Exception:
        return jsonify({"error": "decrypt failed"}), 500
