from functools import wraps
from urllib.parse import urljoin, urlsplit

from flask import flash, redirect, request, url_for
from flask_login import current_user


def build_next_path(req):
    if req.method == "GET":
        return req.full_path.rstrip("?")

    return req.path


def is_safe_next_url(target):
    if not target:
        return False

    ref_url = urlsplit(request.host_url)
    test_url = urlsplit(urljoin(request.host_url, target))
    return test_url.scheme in {"http", "https"} and ref_url.netloc == test_url.netloc


def redirect_to_next(default_endpoint, **values):
    target = request.form.get("next") or request.args.get("next")
    if is_safe_next_url(target):
        return redirect(target)

    return redirect(url_for(default_endpoint, **values))


def ensure_admin_access():
    if not current_user.is_authenticated:
        flash("Please log in to continue.", "error")
        return redirect(url_for("auth.login", next=build_next_path(request)))

    if not current_user.is_admin:
        flash("You do not have permission to access the admin area.", "error")
        return redirect(url_for("main.home"))

    return None


def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        response = ensure_admin_access()
        if response is not None:
            return response

        return view(*args, **kwargs)

    return wrapped_view
