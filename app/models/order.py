from ..extensions import db
from .base import (
    ORDER_STATUSES,
    PAYMENT_METHODS,
    PAYMENT_STATUSES,
    SHIPPING_METHODS,
    TimestampMixin,
    sql_list,
    utc_now,
)


class Order(TimestampMixin, db.Model):
    __tablename__ = "orders"
    __table_args__ = (
        db.CheckConstraint("subtotal >= 0", name="ck_orders_subtotal_non_negative"),
        db.CheckConstraint("shipping_fee >= 0", name="ck_orders_shipping_fee_non_negative"),
        db.CheckConstraint("total_amount >= 0", name="ck_orders_total_amount_non_negative"),
        db.CheckConstraint(
            f"shipping_method IN ({sql_list(SHIPPING_METHODS)})",
            name="ck_orders_shipping_method",
        ),
        db.CheckConstraint(
            f"payment_method IN ({sql_list(PAYMENT_METHODS)})",
            name="ck_orders_payment_method",
        ),
        db.CheckConstraint(
            f"payment_status IN ({sql_list(PAYMENT_STATUSES)})",
            name="ck_orders_payment_status",
        ),
        db.CheckConstraint(
            f"order_status IN ({sql_list(ORDER_STATUSES)})",
            name="ck_orders_order_status",
        ),
        db.Index("ix_orders_user_status", "user_id", "order_status"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    order_number = db.Column(db.String(40), nullable=False, unique=True, index=True)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    shipping_fee = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    shipping_method = db.Column(
        db.String(40),
        nullable=False,
        default="Standard Delivery",
    )
    payment_method = db.Column(
        db.String(40),
        nullable=False,
        default="Cash on Delivery",
    )
    payment_status = db.Column(db.String(20), nullable=False, default="Pending")
    order_status = db.Column(db.String(20), nullable=False, default="Pending", index=True)
    delivery_address = db.Column(db.Text, nullable=False)
    contact_number = db.Column(db.String(30), nullable=False)
    placed_at = db.Column(db.DateTime, nullable=False, default=utc_now, index=True)

    user = db.relationship("User", back_populates="orders")
    items = db.relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class OrderItem(TimestampMixin, db.Model):
    __tablename__ = "order_items"
    __table_args__ = (
        db.CheckConstraint(
            "price_snapshot >= 0",
            name="ck_order_items_price_snapshot_non_negative",
        ),
        db.CheckConstraint(
            "quantity > 0",
            name="ck_order_items_quantity_positive",
        ),
        db.CheckConstraint(
            "line_total >= 0",
            name="ck_order_items_line_total_non_negative",
        ),
        db.Index("ix_order_items_order_product", "order_id", "product_id"),
    )

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(
        db.Integer,
        db.ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id", ondelete="SET NULL"),
        index=True,
    )
    product_name_snapshot = db.Column(db.String(160), nullable=False)
    price_snapshot = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    line_total = db.Column(db.Numeric(10, 2), nullable=False, default=0)

    order = db.relationship("Order", back_populates="items")
    product = db.relationship("Product", back_populates="order_items")
