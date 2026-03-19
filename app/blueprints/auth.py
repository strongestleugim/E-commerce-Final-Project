from flask import Blueprint, flash, render_template, request
from flask_login import current_user, login_required, login_user, logout_user

from ..auth_utils import redirect_to_next
from ..services.auth_service import (
    authenticate_user,
    register_customer_user,
    validate_login_input,
    validate_registration_input,
)

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect_to_next("main.home")

    form_data = {
        "email": request.values.get("email", "").strip(),
        "next": request.values.get("next", "").strip(),
    }
    errors = {}

    if request.method == "POST":
        data, errors = validate_login_input(request.form)
        form_data["email"] = data["email"]
        form_data["next"] = data["next"]

        if not errors:
            user = authenticate_user(data["email"], data["password"])
            if user is None:
                errors["form"] = "Invalid email or password."
            else:
                login_user(user)
                flash(f"Welcome back, {user.name}.", "success")
                return redirect_to_next("main.home")

    return render_template(
        "auth/login.html",
        page_title="Login",
        errors=errors,
        form_data=form_data,
    )


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect_to_next("main.home")

    form_data = {
        "name": request.values.get("name", "").strip(),
        "email": request.values.get("email", "").strip(),
        "next": request.values.get("next", "").strip(),
    }
    errors = {}

    if request.method == "POST":
        data, errors = validate_registration_input(request.form)
        form_data["name"] = data["name"]
        form_data["email"] = data["email"]
        form_data["next"] = data["next"]

        if not errors:
            user = register_customer_user(
                name=data["name"],
                email=data["email"],
                password=data["password"],
            )
            login_user(user)
            flash("Your customer account has been created.", "success")
            return redirect_to_next("account.profile")

    return render_template(
        "auth/register.html",
        page_title="Register",
        errors=errors,
        form_data=form_data,
    )


@auth_bp.post("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect_to_next("main.home")
