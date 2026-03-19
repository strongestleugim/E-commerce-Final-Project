from ..extensions import db
from .base import TimestampMixin


class CartItem(TimestampMixin, db.Model):
    __tablename__ = "cart_items"
    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "product_id",
            name="uq_cart_items_user_product",
        ),
        db.CheckConstraint(
            "quantity > 0",
            name="ck_cart_items_quantity_positive",
        ),
        db.Index("ix_cart_items_user_created", "user_id", "created_at"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    quantity = db.Column(db.Integer, nullable=False, default=1)

    user = db.relationship("User", back_populates="cart_items")
    product = db.relationship("Product", back_populates="cart_items")

