from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import joinedload

from ..extensions import db
from ..models import Category, Order, Product, User

LOW_STOCK_THRESHOLD = 15


@dataclass(frozen=True)
class AdminDashboardData:
    total_products: int
    total_categories: int
    total_orders: int
    total_customers: int
    recent_orders: list[Order]
    low_stock_products: list[Product]
    low_stock_threshold: int
    dashboard_ready: bool = True


def get_admin_dashboard_data(recent_order_limit=5, low_stock_threshold=LOW_STOCK_THRESHOLD):
    try:
        total_products = _count_rows(Product.id)
        total_categories = _count_rows(Category.id)
        total_orders = _count_rows(Order.id)
        total_customers = _count_customers()
        recent_orders = _get_recent_orders(recent_order_limit)
        low_stock_products = _get_low_stock_products(low_stock_threshold)
    except OperationalError:
        return AdminDashboardData(
            total_products=0,
            total_categories=0,
            total_orders=0,
            total_customers=0,
            recent_orders=[],
            low_stock_products=[],
            low_stock_threshold=low_stock_threshold,
            dashboard_ready=False,
        )

    return AdminDashboardData(
        total_products=total_products,
        total_categories=total_categories,
        total_orders=total_orders,
        total_customers=total_customers,
        recent_orders=recent_orders,
        low_stock_products=low_stock_products,
        low_stock_threshold=low_stock_threshold,
        dashboard_ready=True,
    )


def _count_rows(column):
    stmt = select(func.count(column))
    return db.session.execute(stmt).scalar_one()


def _count_customers():
    stmt = select(func.count(User.id)).where(User.role == "customer")
    return db.session.execute(stmt).scalar_one()


def _get_recent_orders(limit):
    stmt = (
        select(Order)
        .options(joinedload(Order.user))
        .order_by(Order.placed_at.desc(), Order.id.desc())
        .limit(limit)
    )
    return db.session.execute(stmt).scalars().all()


def _get_low_stock_products(threshold):
    stmt = (
        select(Product)
        .options(joinedload(Product.category))
        .where(
            Product.is_active.is_(True),
            Product.stock <= threshold,
        )
        .order_by(Product.stock.asc(), Product.name.asc())
        .limit(6)
    )
    return db.session.execute(stmt).scalars().all()
