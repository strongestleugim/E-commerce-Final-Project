from flask import Blueprint, render_template, request

from ..services.catalog_service import (
    get_active_product_by_slug,
    get_catalog_page_data,
    get_related_products,
    normalize_catalog_filters,
)

shop_bp = Blueprint("shop", __name__)


@shop_bp.get("/shop")
def index():
    filters = normalize_catalog_filters(request.args)
    catalog = get_catalog_page_data(filters)
    return render_template("shop/index.html", page_title="Shop", **catalog)


@shop_bp.get("/products/<slug>")
def detail(slug):
    product = get_active_product_by_slug(slug)
    if product is None:
        return render_template(
            "shop/not_found.html",
            page_title="Product Not Found",
            missing_slug=slug,
        ), 404

    related_products = get_related_products(product)

    return render_template(
        "shop/detail.html",
        page_title=product.name,
        product=product,
        related_products=related_products,
    )
