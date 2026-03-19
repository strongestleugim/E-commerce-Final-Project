from ..extensions import db
from .base import TimestampMixin


class Category(TimestampMixin, db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True, index=True)
    description = db.Column(db.Text)
    slug = db.Column(db.String(140), nullable=False, unique=True, index=True)

    products = db.relationship("Product", back_populates="category")

