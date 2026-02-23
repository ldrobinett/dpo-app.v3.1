from functools import wraps
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_login import login_user, logout_user, login_required, current_user

from extensions import db, bcrypt
from models import OperatorUser, ManagedStore, User

operator_bp = Blueprint("operator", __name__, url_prefix="/operator")


# ---------------------------
# Auth helpers
# ---------------------------

def operator_required() -> bool:
    if not getattr(current_user, "is_authenticated", False):
        return False
    return getattr(current_user, "is_operator", False) is True


def operator_only(view_func):
    """Decorator: require operator identity."""
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not getattr(current_user, "is_authenticated", False):
            return redirect(url_for("operator.login"))
        if not operator_required():
            abort(403)
        return view_func(*args, **kwargs)
    return wrapped


def _get_store_or_404(store_id: int) -> ManagedStore:
    s = db.session.get(ManagedStore, store_id)
    if not s:
        abort(404)
    return s


def _operator_pw_ok(pw: str) -> bool:
    return bool(pw) and current_user.check_password(bcrypt, pw)


# ---------------------------
# Auth routes
# ---------------------------

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


# ---------------------------
# Store views
# ---------------------------

@operator_bp.route("/stores", methods=["GET"])
@login_required
@operator_only
def store_index():
    # Active + Archived only (deleted hidden)
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

        # Recommend forcing new stores to active unless you truly need otherwise
        if status not in ("active", "archived"):
            status = "active"

        store = ManagedStore(
            name=name,
            environment=environment,
            status=status,
            url=url,
            admin_username=admin_username,
        )
        store.set_admin_password(admin_password)

        try:
            with db.session.begin():
                db.session.add(store)
                db.session.flush()  # get store.id

                admin_user = User(
                    username=admin_username,
                    password=bcrypt.generate_password_hash(admin_password).decode("utf-8"),
                    store_id=store.id
                )
                db.session.add(admin_user)

            flash("Store and admin user created.", "success")
            return redirect(url_for("operator.store_index"))

        except Exception:
            db.session.rollback()
            flash("Failed to create store.", "danger")
            return redirect(url_for("operator.store_new"))

    return render_template("operator/store_form.html", title="Add Store", store=None)


@operator_bp.route("/stores/<int:store_id>/edit", methods=["GET", "POST"])
@login_required
@operator_only
def store_edit(store_id: int):
    s = _get_store_or_404(store_id)

    if request.method == "POST":
        s.name = (request.form.get("name") or "").strip()
        s.environment = (request.form.get("environment") or s.environment).strip()

        new_status = (request.form.get("status") or s.status).strip()
        # Prevent editing deleted from this screen (do it through lifecycle buttons)
        if s.status != "deleted" and new_status in ("active", "archived"):
            s.status = new_status

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


@operator_bp.route("/stores/<int:store_id>/open", methods=["GET"])
@login_required
@operator_only
def open_store(store_id: int):
    store = _get_store_or_404(store_id)

    if store.status != "active":
        flash("Only active stores can be opened.", "warning")
        return redirect(url_for("operator.store_index"))

    # IMPORTANT: destroy operator session (your intended behavior)
    logout_user()

    return redirect(store.url.rstrip("/") + "/login")


# ---------------------------
# Store lifecycle routes
# ---------------------------

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

    # If your model has deleted_at, clear it too
    if hasattr(store, "deleted_at"):
        store.deleted_at = None

    db.session.commit()
    flash("Store restored.", "success")

    # restore might happen from deleted view
    return redirect(request.referrer or url_for("operator.store_index"))


@operator_bp.route("/stores/<int:store_id>/delete", methods=["POST"])
@login_required
@operator_only
def store_soft_delete(store_id: int):
    """
    Soft delete: mark store deleted. (This replaces your old 'purge' which wasn't a purge.)
    Recommended: require archived first.
    """
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
    """
    Real purge: deletes store row + store users.
    Dev-only by default (blocks prod).
    Requires store already soft-deleted.
    """
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
        with db.session.begin():
            # Delete store-owned users
            User.query.filter(User.store_id == store.id).delete(synchronize_session=False)

            # TODO: delete other store-owned tables here
            # Example:
            # Order.query.filter_by(store_id=store.id).delete(synchronize_session=False)

            db.session.delete(store)

        flash("Store fully purged (store + users).", "danger")
        return redirect(url_for("operator.store_index"))

    except Exception:
        db.session.rollback()
        flash("Purge failed. Nothing partially committed.", "danger")
        return redirect(request.referrer or url_for("operator.store_deleted_index"))


# ---------------------------
# Sensitive action: reveal store admin password
# ---------------------------

@operator_bp.route("/stores/<int:store_id>/reveal", methods=["POST"])
@login_required
@operator_only
def store_reveal(store_id: int):
    """
    Reveal store admin password ONLY after re-confirming operator password.
    Returns JSON: {password: "..."}.
    """
    operator_password = request.form.get("operator_password") or ""
    if not _operator_pw_ok(operator_password):
        return jsonify({"error": "bad operator password"}), 401

    s = _get_store_or_404(store_id)

    # Optional: block revealing for deleted stores
    if getattr(s, "status", None) == "deleted":
        return jsonify({"error": "store deleted"}), 400

    try:
        pw = s.get_admin_password()
        return jsonify({"password": pw})
    except Exception:
        return jsonify({"error": "decrypt failed"}), 500
