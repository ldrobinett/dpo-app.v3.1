from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db, bcrypt
from models import User, Role
from utils.permissions import require_capability
from forms import UserCreationForm

users_bp = Blueprint("users", __name__)

# ================================
# LIST USERS
# ================================
@users_bp.route("/users")
@login_required
@require_capability("users.manage")
def list_users():
    users = User.query.filter_by(store_id=current_user.store_id).all()
    roles = Role.query.filter_by(store_id=current_user.store_id).all()

    return render_template(
        "users.html",
        title="Users",
        users=users,
        roles=roles,
    )

# ================================
# CREATE USER
# ================================
@users_bp.route("/users/new", methods=["GET", "POST"])
@login_required
@require_capability("users.manage")
def create_user():

    roles = Role.query.filter_by(store_id=current_user.store_id).all()

    # Safety check
    if not roles:
        flash("No roles found for this store. Contact support.", "danger")
        return redirect(url_for("users.list_users"))

    form = UserCreationForm()
    form.roles.choices = [(r.id, r.name) for r in roles]

    if form.validate_on_submit():

        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode("utf-8")

        user = User(
            username=form.username.data,
            password=hashed_pw,
            store_id=current_user.store_id,
        )

        for role_id in form.roles.data:
            role = Role.query.get(role_id)
            if role:
                user.roles.append(role)

        db.session.add(user)
        db.session.commit()

        flash("User created successfully", "success")
        return redirect(url_for("users.list_users"))

    return render_template("create_user.html", form=form)



# ================================
# TOGGLE ACTIVE
# ================================
@users_bp.route("/users/<int:user_id>/toggle", methods=["POST"])
@login_required
@require_capability("users.manage")
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)

    if user.store_id != current_user.store_id:
        flash("Unauthorized", "danger")
        return redirect(url_for("users.list_users"))

    user.is_active = not user.is_active
    db.session.commit()

    flash("User status updated", "success")
    return redirect(url_for("users.list_users"))

# ================================
# Edit Users
# ================================
@users_bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
@require_capability("users.manage")
def edit_user(user_id):

    user = User.query.get_or_404(user_id)

    if user.store_id != current_user.store_id:
        flash("Unauthorized", "danger")
        return redirect(url_for("users.list_users"))

    roles = Role.query.filter_by(store_id=current_user.store_id).all()

    if request.method == "POST":
        selected_role_ids = request.form.getlist("roles")

        user.roles = Role.query.filter(
            Role.id.in_(selected_role_ids),
            Role.store_id == current_user.store_id
        ).all()

        db.session.commit()
        flash("User updated successfully.", "success")
        return redirect(url_for("users.list_users"))

    return render_template(
        "edit_user.html",
        user=user,
        roles=roles,
    )

