import re
from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import func, select

from ..extensions import db
from ..models import Order, OrderItem
from ..models.base import PAYMENT_METHODS, SHIPPING_METHODS, utc_now
from .cart_service import get_cart_snapshot

CONTACT_PATTERN = re.compile(r"^[0-9+() -]{7,20}$")
SHIPPING_FEES = {
    "Standard Delivery": Decimal("99.00"),
    "Express Delivery": Decimal("199.00"),
    "Store Pickup": Decimal("0.00"),
}


@dataclass(frozen=True)
class CheckoutOption:
    label: str
    fee: Decimal | None = None


def build_checkout_context(user_id, form_data=None, errors=None):
    cart = get_cart_snapshot(user_id)
    form_data = _merge_checkout_defaults(form_data or {}, apply_defaults=form_data is None)
    shipping_fee = get_shipping_fee(form_data["shipping_method"])
    total_amount = cart.subtotal + shipping_fee

    return {
        "cart": cart,
        "errors": errors or {},
        "form_data": form_data,
        "shipping_options": get_shipping_options(),
        "payment_options": get_payment_options(),
        "shipping_fee": shipping_fee,
        "total_amount": total_amount,
    }


def validate_checkout_input(form_data, user_id):
    cart = get_cart_snapshot(user_id)
    data = {
        "delivery_address": form_data.get("delivery_address", "").strip(),
        "contact_number": form_data.get("contact_number", "").strip(),
        "shipping_method": form_data.get("shipping_method", "").strip(),
        "payment_method": form_data.get("payment_method", "").strip(),
    }
    errors = {}

    if not cart.cart_ready:
        errors["form"] = "The cart is not ready yet. Initialize the database and try again."
        return data, errors

    if cart.is_empty:
        errors["form"] = "Your cart is empty. Add products before checking out."
        return data, errors

    if len(data["delivery_address"]) < 10:
        errors["delivery_address"] = "Enter a complete delivery address."
    elif len(data["delivery_address"]) > 500:
        errors["delivery_address"] = "Delivery address must be 500 characters or fewer."

    if not data["contact_number"]:
        errors["contact_number"] = "Enter a contact number."
    elif not CONTACT_PATTERN.match(data["contact_number"]):
        errors["contact_number"] = "Enter a valid contact number."

    if not data["shipping_method"]:
        errors["shipping_method"] = "Choose a shipping method."
    elif data["shipping_method"] not in SHIPPING_METHODS:
        errors["shipping_method"] = "Choose a valid shipping method."

    if not data["payment_method"]:
        errors["payment_method"] = "Choose a payment method."
    elif data["payment_method"] not in PAYMENT_METHODS:
        errors["payment_method"] = "Choose a valid payment method."

    cart_error = _validate_cart_snapshot(cart)
    if cart_error:
        errors["form"] = cart_error

    return data, errors


def place_order(user_id, checkout_data):
    cart = get_cart_snapshot(user_id)

    if not cart.cart_ready:
        raise ValueError("The cart is not ready yet. Initialize the database and try again.")

    if cart.is_empty:
        raise ValueError("Your cart is empty. Add products before checking out.")

    cart_error = _validate_cart_snapshot(cart)
    if cart_error:
        raise ValueError(cart_error)

    shipping_method = checkout_data.get("shipping_method", "").strip()
    payment_method = checkout_data.get("payment_method", "").strip()

    if shipping_method not in SHIPPING_METHODS:
        raise ValueError("Choose a valid shipping method before placing the order.")

    if payment_method not in PAYMENT_METHODS:
        raise ValueError("Choose a valid payment method before placing the order.")

    shipping_fee = get_shipping_fee(shipping_method)
    total_amount = cart.subtotal + shipping_fee

    order = Order(
        user_id=user_id,
        order_number=_generate_order_number(),
        subtotal=cart.subtotal,
        shipping_fee=shipping_fee,
        total_amount=total_amount,
        shipping_method=shipping_method,
        payment_method=payment_method,
        payment_status=_payment_status_for_method(payment_method),
        order_status="Pending",
        delivery_address=checkout_data["delivery_address"],
        contact_number=checkout_data["contact_number"],
        placed_at=utc_now(),
    )
    db.session.add(order)

    for line in cart.lines:
        product = line.item.product
        product.stock -= line.item.quantity

        db.session.add(
            OrderItem(
                order=order,
                product=product,
                product_name_snapshot=product.name,
                price_snapshot=line.unit_price,
                quantity=line.item.quantity,
                line_total=line.line_total,
            )
        )
        db.session.delete(line.item)

    db.session.commit()
    return order


def get_shipping_options():
    return [
        CheckoutOption(label=method, fee=SHIPPING_FEES[method])
        for method in SHIPPING_METHODS
    ]


def get_payment_options():
    return [CheckoutOption(label=method) for method in PAYMENT_METHODS]


def get_shipping_fee(shipping_method):
    return SHIPPING_FEES.get(shipping_method, Decimal("0.00"))


def _merge_checkout_defaults(data, apply_defaults=True):
    shipping_method = data.get("shipping_method", "")
    payment_method = data.get("payment_method", "")

    if apply_defaults:
        shipping_method = shipping_method or "Standard Delivery"
        payment_method = payment_method or "Cash on Delivery"

    return {
        "delivery_address": data.get("delivery_address", ""),
        "contact_number": data.get("contact_number", ""),
        "shipping_method": shipping_method,
        "payment_method": payment_method,
    }


def _validate_cart_snapshot(cart):
    for line in cart.lines:
        product = line.item.product
        if not product.is_active:
            return f"{product.name} is no longer available. Remove it from your cart to continue."

        if line.item.quantity > product.stock:
            return (
                f"{product.name} only has {product.stock} units available. "
                "Update your cart before placing the order."
            )

    return ""


def _payment_status_for_method(payment_method):
    if payment_method in {"Simulated GCash", "Simulated Card"}:
        return "Paid"

    return "Pending"


def _generate_order_number():
    prefix = f"GL-{utc_now().strftime('%Y%m%d')}"
    stmt = select(func.count(Order.id)).where(Order.order_number.like(f"{prefix}-%"))
    next_number = db.session.execute(stmt).scalar_one() + 1

    while True:
        order_number = f"{prefix}-{next_number:04d}"
        exists = Order.query.filter_by(order_number=order_number).first()
        if exists is None:
            return order_number
        next_number += 1
