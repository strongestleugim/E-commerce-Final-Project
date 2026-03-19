from ..extensions import db
from .base import TimestampMixin


class Product(TimestampMixin, db.Model):
    __tablename__ = "products"
    __table_args__ = (
        db.CheckConstraint("price >= 0", name="ck_products_price_non_negative"),
        db.CheckConstraint("stock >= 0", name="ck_products_stock_non_negative"),
        db.Index("ix_products_category_active", "category_id", "is_active"),
    )

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    name = db.Column(db.String(160), nullable=False, index=True)
    slug = db.Column(db.String(180), nullable=False, unique=True, index=True)
    short_description = db.Column(db.String(255), nullable=False)
    full_description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    stock = db.Column(db.Integer, nullable=False, default=0)
    flavor_or_variant = db.Column(db.String(120))
    size_or_weight = db.Column(db.String(120))
    image_path = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, nullable=False, default=True, index=True)

    category = db.relationship("Category", back_populates="products")
    cart_items = db.relationship(
        "CartItem",
        back_populates="product",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    order_items = db.relationship("OrderItem", back_populates="product")

