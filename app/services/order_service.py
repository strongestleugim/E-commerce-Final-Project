from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from ..extensions import db
from ..models import Order, OrderItem


def get_orders_for_user(user_id):
    stmt = (
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.user_id == user_id)
        .order_by(Order.placed_at.desc(), Order.id.desc())
    )
    return db.session.execute(stmt).scalars().all()


def get_order_for_user(user_id, order_number):
    stmt = (
        select(Order)
        .options(
            selectinload(Order.items).joinedload(OrderItem.product),
            joinedload(Order.user),
        )
        .where(
            Order.user_id == user_id,
            Order.order_number == order_number,
        )
    )
    return db.session.execute(stmt).scalar_one_or_none()
