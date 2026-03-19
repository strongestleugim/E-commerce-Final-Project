from datetime import datetime

from ..extensions import db

USER_ROLES = ("customer", "admin")
SHIPPING_METHODS = (
    "Standard Delivery",
    "Express Delivery",
    "Store Pickup",
)
PAYMENT_METHODS = (
    "Cash on Delivery",
    "Simulated GCash",
    "Simulated Card",
)
PAYMENT_STATUSES = ("Pending", "Paid", "Failed", "Cancelled")
ORDER_STATUSES = ("Pending", "Confirmed", "Shipped", "Delivered", "Cancelled")


def utc_now():
    return datetime.utcnow()


def sql_list(values):
    return ", ".join(repr(value) for value in values)


class TimestampMixin:
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )

