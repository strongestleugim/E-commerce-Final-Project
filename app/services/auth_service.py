import re

from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import db
from ..models import User

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_registration_input(form_data):
    data = {
        "name": form_data.get("name", "").strip(),
        "email": normalize_email(form_data.get("email", "")),
        "password": form_data.get("password", ""),
        "confirm_password": form_data.get("confirm_password", ""),
        "next": form_data.get("next", "").strip(),
    }
    errors = {}

    if len(data["name"]) < 2:
        errors["name"] = "Enter your full name."
    elif len(data["name"]) > 120:
        errors["name"] = "Name must be 120 characters or fewer."

    if not data["email"]:
        errors["email"] = "Enter your email address."
    elif not EMAIL_PATTERN.match(data["email"]):
        errors["email"] = "Enter a valid email address."
    elif User.query.filter_by(email=data["email"]).first():
        errors["email"] = "An account with that email already exists."

    if len(data["password"]) < 8:
        errors["password"] = "Password must be at least 8 characters."

    if data["password"] != data["confirm_password"]:
        errors["confirm_password"] = "Passwords do not match."

    return data, errors


def validate_login_input(form_data):
    data = {
        "email": normalize_email(form_data.get("email", "")),
        "password": form_data.get("password", ""),
        "next": form_data.get("next", "").strip(),
    }
    errors = {}

    if not data["email"]:
        errors["email"] = "Enter your email address."
    elif not EMAIL_PATTERN.match(data["email"]):
        errors["email"] = "Enter a valid email address."

    if not data["password"]:
        errors["password"] = "Enter your password."

    return data, errors


def register_customer_user(name, email, password):
    user = User(
        name=name,
        email=normalize_email(email),
        password_hash=generate_password_hash(password),
        role="customer",
    )
    db.session.add(user)
    db.session.commit()
    return user


def authenticate_user(email, password):
    user = User.query.filter_by(email=normalize_email(email)).one_or_none()
    if user is None:
        return None

    if not check_password_hash(user.password_hash, password):
        return None

    return user


def normalize_email(value):
    return value.strip().lower()
