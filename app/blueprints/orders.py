from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from ..services.order_service import get_order_for_user, get_orders_for_user

orders_bp = Blueprint("orders", __name__)


@orders_bp.before_request
def protect_customer_order_routes():
    if current_user.is_authenticated and current_user.is_admin:
        flash("Admin accounts do not use the customer order history area.", "error")
        return redirect(url_for("admin.dashboard"))


@orders_bp.get("/orders")
@login_required
def index():
    orders = get_orders_for_user(current_user.id)
    return render_template("orders/index.html", page_title="Orders", orders=orders)


@orders_bp.get("/orders/<order_number>")
@login_required
def detail(order_number):
    order = get_order_for_user(current_user.id, order_number)
    if order is None:
        return render_template(
            "orders/not_found.html",
            page_title="Order Not Found",
            missing_order_number=order_number,
        ), 404

    return render_template(
        "orders/detail.html",
        page_title=f"Order {order.order_number}",
        order=order,
    )
