from flask_login import UserMixin

from ..extensions import db
from .base import TimestampMixin, USER_ROLES, sql_list


class User(UserMixin, TimestampMixin, db.Model):
    __tablename__ = "users"
    __table_args__ = (
        db.CheckConstraint(
            f"role IN ({sql_list(USER_ROLES)})",
            name="ck_users_role",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="customer", index=True)

    cart_items = db.relationship(
        "CartItem",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    orders = db.relationship("Order", back_populates="user")

    @property
    def is_admin(self):
        return self.role == "admin"
