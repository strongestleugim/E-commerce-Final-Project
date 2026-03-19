from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..services.checkout_service import build_checkout_context, place_order, validate_checkout_input
from ..services.order_service import get_order_for_user

checkout_bp = Blueprint("checkout", __name__)


@checkout_bp.route("/checkout", methods=["GET", "POST"])
@login_required
def index():
    if current_user.is_admin:
        flash("Admin accounts cannot place customer orders.", "error")
        return redirect(url_for("main.home"))

    if request.method == "POST":
        form_data, errors = validate_checkout_input(request.form, current_user.id)
        if not errors:
            try:
                order = place_order(current_user.id, form_data)
            except ValueError as exc:
                errors["form"] = str(exc)
            else:
                flash(f"Order {order.order_number} placed successfully.", "success")
                return redirect(
                    url_for("checkout.confirmation", order_number=order.order_number)
                )

        context = build_checkout_context(current_user.id, form_data=form_data, errors=errors)
        return render_template("checkout/index.html", page_title="Checkout", **context)

    context = build_checkout_context(current_user.id)
    return render_template("checkout/index.html", page_title="Checkout", **context)


@checkout_bp.get("/checkout/confirmation/<order_number>")
@login_required
def confirmation(order_number):
    order = get_order_for_user(current_user.id, order_number)
    if order is None:
        return render_template(
            "orders/not_found.html",
            page_title="Order Not Found",
            missing_order_number=order_number,
        ), 404

    return render_template(
        "checkout/confirmation.html",
        page_title=f"Order {order.order_number}",
        order=order,
    )
