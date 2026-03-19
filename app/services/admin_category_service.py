import re
from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from ..extensions import db
from ..models import Category, Product


@dataclass(frozen=True)
class AdminCategoryRow:
    category: Category
    usage_count: int


def list_admin_category_rows():
    stmt = (
        select(
            Category,
            func.count(Product.id).label("usage_count"),
        )
        .outerjoin(Product, Product.category_id == Category.id)
        .group_by(Category.id)
        .order_by(Category.name.asc())
    )
    rows = db.session.execute(stmt).all()
    return [
        AdminCategoryRow(
            category=row.Category,
            usage_count=row.usage_count,
        )
        for row in rows
    ]


def get_admin_category(category_id):
    stmt = (
        select(Category)
        .options(selectinload(Category.products))
        .where(Category.id == category_id)
    )
    return db.session.execute(stmt).scalar_one_or_none()


def get_category_usage_count(category_id):
    stmt = select(func.count(Product.id)).where(Product.category_id == category_id)
    return db.session.execute(stmt).scalar_one()


def get_category_form_defaults(category=None):
    if category is None:
        return {
            "name": "",
            "slug": "",
            "description": "",
        }

    return {
        "name": category.name,
        "slug": category.slug,
        "description": category.description or "",
    }


def extract_category_form_data(form):
    return {
        "name": form.get("name", "").strip(),
        "slug": form.get("slug", "").strip(),
        "description": form.get("description", "").strip(),
    }


def validate_category_form_data(form_data, existing_category=None):
    errors = {}
    normalized = {
        "name": form_data["name"],
        "slug": normalize_slug(form_data["slug"]) or slugify(form_data["name"]),
        "description": form_data["description"],
    }

    if len(normalized["name"]) < 2:
        errors["name"] = "Category name must be at least 2 characters."
    elif len(normalized["name"]) > 120:
        errors["name"] = "Category name must be 120 characters or fewer."
    else:
        existing_name = (
            db.session.execute(
                select(Category).where(func.lower(Category.name) == normalized["name"].lower())
            )
            .scalar_one_or_none()
        )
        if existing_name is not None and (
            existing_category is None or existing_name.id != existing_category.id
        ):
            errors["name"] = "A category with that name already exists."

    if not normalized["slug"]:
        errors["slug"] = "Enter a slug or use a name that can generate one."
    elif len(normalized["slug"]) > 140:
        errors["slug"] = "Slug must be 140 characters or fewer."
    else:
        existing_slug = Category.query.filter_by(slug=normalized["slug"]).one_or_none()
        if existing_slug is not None and (
            existing_category is None or existing_slug.id != existing_category.id
        ):
            errors["slug"] = "A category with that slug already exists."

    if len(normalized["description"]) > 1000:
        errors["description"] = "Description must be 1000 characters or fewer."

    return normalized, errors


def create_category(data):
    category = Category(
        name=data["name"],
        slug=data["slug"],
        description=data["description"] or None,
    )
    db.session.add(category)
    db.session.commit()
    return category


def update_category(category, data):
    category.name = data["name"]
    category.slug = data["slug"]
    category.description = data["description"] or None
    db.session.commit()
    return category


def slugify(value):
    return normalize_slug(value)


def normalize_slug(value):
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value)
    return value.strip("-")
