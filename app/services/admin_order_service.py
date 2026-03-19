from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from ..extensions import db
from ..models import Order, OrderItem
from ..models.base import ORDER_STATUSES, PAYMENT_STATUSES

ALLOWED_ORDER_TRANSITIONS = {
    "Pending": ("Confirmed", "Shipped", "Cancelled"),
    "Confirmed": ("Shipped", "Cancelled"),
    "Shipped": ("Delivered",),
    "Delivered": (),
    "Cancelled": (),
}


def list_admin_orders():
    stmt = (
        select(Order)
        .options(
            joinedload(Order.user),
            selectinload(Order.items),
        )
        .order_by(Order.placed_at.desc(), Order.id.desc())
    )
    return db.session.execute(stmt).scalars().all()


def get_admin_order(order_number):
    stmt = (
        select(Order)
        .options(
            joinedload(Order.user),
            selectinload(Order.items).joinedload(OrderItem.product),
        )
        .where(Order.order_number == order_number)
    )
    return db.session.execute(stmt).scalar_one_or_none()


def get_order_status_choices(order):
    return [order.order_status, *ALLOWED_ORDER_TRANSITIONS.get(order.order_status, ())]


def get_payment_status_choices():
    return list(PAYMENT_STATUSES)


def update_admin_order_status(order, new_status):
    error = validate_order_status_transition(order, new_status)
    if error:
        raise ValueError(error)

    order.order_status = new_status
    if new_status == "Cancelled" and order.payment_status == "Pending":
        order.payment_status = "Cancelled"

    db.session.commit()
    return order


def update_admin_payment_status(order, new_status):
    if new_status not in PAYMENT_STATUSES:
        raise ValueError("Choose a valid payment status.")

    if order.order_status == "Cancelled" and new_status == "Paid":
        raise ValueError("Cancelled orders cannot be marked as paid.")

    order.payment_status = new_status
    db.session.commit()
    return order


def validate_order_status_transition(order, new_status):
    if new_status not in ORDER_STATUSES:
        return "Choose a valid order status."

    if new_status == order.order_status:
        return ""

    allowed_statuses = ALLOWED_ORDER_TRANSITIONS.get(order.order_status, ())
    if new_status not in allowed_statuses:
        return (
            f"Cannot change status from {order.order_status} to {new_status}. "
            "Use the next valid step in the order flow."
        )

    return ""
