from flask import Blueprint, render_template
from flask_login import current_user, login_required

account_bp = Blueprint("account", __name__)


@account_bp.get("/profile")
@login_required
def profile():
    return render_template(
        "account/profile.html",
        page_title="Profile",
        profile_user=current_user,
    )
