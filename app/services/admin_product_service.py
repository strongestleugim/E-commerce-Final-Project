import re
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from uuid import uuid4

from flask import current_app
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from ..extensions import db
from ..models import Category, Product

ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif", "svg"}
PLACEHOLDER_IMAGE_BY_CATEGORY = {
    "protein": "img/products/protein-placeholder.svg",
    "pre-workout": "img/products/pre-workout-placeholder.svg",
    "creatine": "img/products/creatine-placeholder.svg",
    "recovery": "img/products/recovery-placeholder.svg",
    "bundles": "img/products/bundles-placeholder.svg",
    "accessories": "img/products/accessories-placeholder.svg",
}


def list_admin_products():
    stmt = (
        select(Product)
        .options(joinedload(Product.category))
        .order_by(Product.updated_at.desc(), Product.name.asc())
    )
    return db.session.execute(stmt).scalars().all()


def list_admin_categories():
    stmt = select(Category).order_by(Category.name.asc())
    return db.session.execute(stmt).scalars().all()


def get_admin_product(product_id):
    stmt = (
        select(Product)
        .options(joinedload(Product.category))
        .where(Product.id == product_id)
    )
    return db.session.execute(stmt).scalar_one_or_none()


def get_product_form_defaults(product=None):
    if product is None:
        return {
            "category_id": "",
            "name": "",
            "slug": "",
            "short_description": "",
            "full_description": "",
            "price": "",
            "stock": "0",
            "flavor_or_variant": "",
            "size_or_weight": "",
            "is_active": True,
        }

    return {
        "category_id": str(product.category_id),
        "name": product.name,
        "slug": product.slug,
        "short_description": product.short_description,
        "full_description": product.full_description,
        "price": f"{product.price:.2f}",
        "stock": str(product.stock),
        "flavor_or_variant": product.flavor_or_variant or "",
        "size_or_weight": product.size_or_weight or "",
        "is_active": product.is_active,
    }


def extract_product_form_data(form):
    return {
        "category_id": form.get("category_id", "").strip(),
        "name": form.get("name", "").strip(),
        "slug": form.get("slug", "").strip(),
        "short_description": form.get("short_description", "").strip(),
        "full_description": form.get("full_description", "").strip(),
        "price": form.get("price", "").strip(),
        "stock": form.get("stock", "").strip(),
        "flavor_or_variant": form.get("flavor_or_variant", "").strip(),
        "size_or_weight": form.get("size_or_weight", "").strip(),
        "is_active": form.get("is_active") == "on",
    }


def validate_product_form_data(form_data, image_file=None, existing_product=None):
    errors = {}
    normalized = {
        "name": form_data["name"],
        "slug": normalize_slug(form_data["slug"]) or slugify(form_data["name"]),
        "short_description": form_data["short_description"],
        "full_description": form_data["full_description"],
        "flavor_or_variant": form_data["flavor_or_variant"],
        "size_or_weight": form_data["size_or_weight"],
        "is_active": form_data["is_active"],
    }

    if len(normalized["name"]) < 3:
        errors["name"] = "Name must be at least 3 characters."
    elif len(normalized["name"]) > 160:
        errors["name"] = "Name must be 160 characters or fewer."

    if not normalized["slug"]:
        errors["slug"] = "Enter a slug or use a name that can generate one."
    elif len(normalized["slug"]) > 180:
        errors["slug"] = "Slug must be 180 characters or fewer."
    else:
        existing_slug = Product.query.filter_by(slug=normalized["slug"]).one_or_none()
        if existing_slug is not None and (
            existing_product is None or existing_slug.id != existing_product.id
        ):
            errors["slug"] = "A product with that slug already exists."

    category = _parse_category(form_data["category_id"])
    if category is None:
        errors["category_id"] = "Choose a valid category."
    else:
        normalized["category"] = category

    if len(normalized["short_description"]) < 12:
        errors["short_description"] = "Short description must be at least 12 characters."
    elif len(normalized["short_description"]) > 255:
        errors["short_description"] = "Short description must be 255 characters or fewer."

    if len(normalized["full_description"]) < 24:
        errors["full_description"] = "Full description must be at least 24 characters."

    if len(normalized["flavor_or_variant"]) > 120:
        errors["flavor_or_variant"] = "Flavor or variant must be 120 characters or fewer."

    if len(normalized["size_or_weight"]) > 120:
        errors["size_or_weight"] = "Size or weight must be 120 characters or fewer."

    price = _parse_price(form_data["price"])
    if price is None:
        errors["price"] = "Enter a valid non-negative price."
    else:
        normalized["price"] = price

    stock = _parse_stock(form_data["stock"])
    if stock is None:
        errors["stock"] = "Enter a valid stock quantity of 0 or more."
    else:
        normalized["stock"] = stock

    image_error = validate_image_file(image_file)
    if image_error:
        errors["image_file"] = image_error

    return normalized, errors


def create_product(data, image_file=None):
    product = Product(
        category=data["category"],
        name=data["name"],
        slug=data["slug"],
        short_description=data["short_description"],
        full_description=data["full_description"],
        price=data["price"],
        stock=data["stock"],
        flavor_or_variant=data["flavor_or_variant"] or None,
        size_or_weight=data["size_or_weight"] or None,
        is_active=data["is_active"],
    )

    product.image_path = _resolve_image_path(
        image_file=image_file,
        slug=product.slug,
        category_slug=product.category.slug,
    )

    db.session.add(product)
    db.session.commit()
    return product


def update_product(product, data, image_file=None):
    category_changed = product.category_id != data["category"].id

    product.category = data["category"]
    product.name = data["name"]
    product.slug = data["slug"]
    product.short_description = data["short_description"]
    product.full_description = data["full_description"]
    product.price = data["price"]
    product.stock = data["stock"]
    product.flavor_or_variant = data["flavor_or_variant"] or None
    product.size_or_weight = data["size_or_weight"] or None
    product.is_active = data["is_active"]

    if image_file is not None and image_file.filename:
        product.image_path = _save_image_file(image_file, product.slug)
    elif not product.image_path or (category_changed and _is_placeholder_path(product.image_path)):
        product.image_path = placeholder_image_path(product.category.slug)

    db.session.commit()
    return product


def toggle_product_active(product):
    product.is_active = not product.is_active
    db.session.commit()
    return product.is_active


def slugify(value):
    slug = normalize_slug(value)
    return slug


def normalize_slug(value):
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value)
    return value.strip("-")


def placeholder_image_path(category_slug):
    return PLACEHOLDER_IMAGE_BY_CATEGORY.get(category_slug, "img/products/protein-placeholder.svg")


def validate_image_file(image_file):
    if image_file is None or not image_file.filename:
        return ""

    extension = Path(image_file.filename).suffix.lower().lstrip(".")
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_IMAGE_EXTENSIONS))
        return f"Upload a supported image type: {allowed}."

    return ""


def _parse_category(category_id):
    try:
        parsed_id = int(category_id)
    except (TypeError, ValueError):
        return None

    return db.session.get(Category, parsed_id)


def _parse_price(value):
    try:
        amount = Decimal(value)
    except (InvalidOperation, TypeError):
        return None

    if amount < 0:
        return None

    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _parse_stock(value):
    try:
        amount = int(value)
    except (TypeError, ValueError):
        return None

    if amount < 0:
        return None

    return amount


def _resolve_image_path(image_file, slug, category_slug):
    if image_file is not None and image_file.filename:
        return _save_image_file(image_file, slug)

    return placeholder_image_path(category_slug)


def _save_image_file(image_file: FileStorage, slug):
    upload_dir = Path(current_app.config["PRODUCT_IMAGE_UPLOAD_DIR"])
    upload_dir.mkdir(parents=True, exist_ok=True)

    filename = secure_filename(image_file.filename or "")
    extension = Path(filename).suffix.lower()
    stem = secure_filename(slug) or "product"
    generated_name = f"{stem}-{uuid4().hex[:8]}{extension}"
    target_path = upload_dir / generated_name

    image_file.save(target_path)

    web_root = current_app.config["PRODUCT_IMAGE_UPLOAD_WEB_PATH"].strip("/")
    return f"{web_root}/{generated_name}"


def _is_placeholder_path(image_path):
    return image_path.startswith("img/products/") and image_path.endswith("-placeholder.svg")
