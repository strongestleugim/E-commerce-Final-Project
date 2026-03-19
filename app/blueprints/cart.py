from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user

from ..auth_utils import redirect_to_next
from ..services.cart_service import (
    add_product_to_cart,
    get_cart_snapshot,
    remove_cart_item,
    update_cart_item_quantity,
)

cart_bp = Blueprint("cart", __name__)


@cart_bp.get("/cart")
def index():
    auth_redirect = _ensure_cart_access(url_for("cart.index"))
    if auth_redirect is not None:
        return auth_redirect

    cart = get_cart_snapshot(current_user.id)
    return render_template("cart/index.html", page_title="Cart", cart=cart)


@cart_bp.post("/cart/add")
def add():
    auth_redirect = _ensure_cart_access(request.form.get("origin") or url_for("cart.index"))
    if auth_redirect is not None:
        return auth_redirect

    product_id = request.form.get("product_id", type=int)
    quantity = request.form.get("quantity", type=int)

    if product_id is None:
        abort(404)

    try:
        message = add_product_to_cart(current_user.id, product_id, quantity)
    except LookupError:
        abort(404)
    except ValueError as exc:
        flash(str(exc), "error")
    else:
        flash(message, "success")

    return redirect_to_next("cart.index")


@cart_bp.post("/cart/items/<int:item_id>/update")
def update(item_id):
    auth_redirect = _ensure_cart_access(url_for("cart.index"))
    if auth_redirect is not None:
        return auth_redirect

    quantity = request.form.get("quantity", type=int)

    try:
        message = update_cart_item_quantity(current_user.id, item_id, quantity)
    except LookupError:
        abort(404)
    except ValueError as exc:
        flash(str(exc), "error")
    else:
        flash(message, "success")

    return redirect_to_next("cart.index")


@cart_bp.post("/cart/items/<int:item_id>/remove")
def remove(item_id):
    auth_redirect = _ensure_cart_access(url_for("cart.index"))
    if auth_redirect is not None:
        return auth_redirect

    try:
        message = remove_cart_item(current_user.id, item_id)
    except LookupError:
        abort(404)
    else:
        flash(message, "success")

    return redirect_to_next("cart.index")


def _ensure_cart_access(next_target):
    if not current_user.is_authenticated:
        flash("Please log in to use your cart.", "error")
        return redirect(url_for("auth.login", next=next_target))

    if current_user.is_admin:
        flash("Admin accounts cannot use the customer cart.", "error")
        return redirect(url_for("admin.dashboard"))

    if current_user.is_authenticated:
        return None
