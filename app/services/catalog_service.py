from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import joinedload

from ..extensions import db
from ..models import Category, Product


@dataclass(frozen=True)
class CatalogFilters:
    search_query: str = ""
    category_slug: str = ""

    @property
    def has_filters(self):
        return bool(self.search_query or self.category_slug)


@dataclass(frozen=True)
class CategoryOption:
    id: int
    name: str
    slug: str
    product_count: int


def normalize_catalog_filters(args):
    return CatalogFilters(
        search_query=args.get("q", "").strip(),
        category_slug=args.get("category", "").strip().lower(),
    )


def get_catalog_page_data(filters):
    try:
        categories = _get_category_options()
        products = _get_active_products(filters)
    except OperationalError:
        return {
            "filters": filters,
            "categories": [],
            "products": [],
            "selected_category": None,
            "catalog_ready": False,
        }

    selected_category = next(
        (category for category in categories if category.slug == filters.category_slug),
        None,
    )

    return {
        "filters": filters,
        "categories": categories,
        "products": products,
        "selected_category": selected_category,
        "catalog_ready": True,
    }


def get_active_product_by_slug(slug):
    try:
        stmt = (
            select(Product)
            .options(joinedload(Product.category))
            .where(
                Product.slug == slug,
                Product.is_active.is_(True),
            )
        )
        return db.session.execute(stmt).scalar_one_or_none()
    except OperationalError:
        return None


def get_related_products(product, limit=3):
    try:
        stmt = (
            select(Product)
            .options(joinedload(Product.category))
            .where(
                Product.is_active.is_(True),
                Product.category_id == product.category_id,
                Product.id != product.id,
            )
            .order_by(Product.name.asc())
            .limit(limit)
        )
        return db.session.execute(stmt).scalars().all()
    except OperationalError:
        return []


def _get_category_options():
    stmt = (
        select(
            Category.id,
            Category.name,
            Category.slug,
            func.count(Product.id).label("product_count"),
        )
        .join(Product, Product.category_id == Category.id)
        .where(Product.is_active.is_(True))
        .group_by(Category.id, Category.name, Category.slug)
        .order_by(Category.name.asc())
    )

    rows = db.session.execute(stmt).all()
    return [
        CategoryOption(
            id=row.id,
            name=row.name,
            slug=row.slug,
            product_count=row.product_count,
        )
        for row in rows
    ]


def _get_active_products(filters):
    stmt = (
        select(Product)
        .join(Product.category)
        .options(joinedload(Product.category))
        .where(Product.is_active.is_(True))
        .order_by(Category.name.asc(), Product.name.asc())
    )

    if filters.category_slug:
        stmt = stmt.where(Category.slug == filters.category_slug)

    if filters.search_query:
        stmt = stmt.where(Product.name.ilike(f"%{filters.search_query}%"))

    return db.session.execute(stmt).scalars().all()
