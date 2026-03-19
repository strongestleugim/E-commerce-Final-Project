from flask import Blueprint, flash, render_template, request
from flask_login import current_user

from ..auth_utils import ensure_admin_access, redirect_to_next
from ..services.admin_category_service import (
    create_category,
    extract_category_form_data,
    get_admin_category,
    get_category_form_defaults,
    get_category_usage_count,
    list_admin_category_rows,
    update_category,
    validate_category_form_data,
)
from ..services.admin_order_service import (
    get_admin_order,
    get_order_status_choices,
    get_payment_status_choices,
    list_admin_orders,
    update_admin_order_status,
    update_admin_payment_status,
)
from ..services.admin_product_service import (
    create_product,
    extract_product_form_data,
    get_admin_product,
    get_product_form_defaults,
    list_admin_categories,
    list_admin_products,
    toggle_product_active,
    update_product,
    validate_product_form_data,
)
from ..services.admin_service import get_admin_dashboard_data

admin_bp = Blueprint("admin", __name__)


@admin_bp.before_request
def protect_admin_routes():
    return ensure_admin_access()


@admin_bp.get("/admin")
def dashboard():
    dashboard_data = get_admin_dashboard_data()
    return render_template(
        "admin/dashboard.html",
        page_title="Admin Dashboard",
        admin_user=current_user,
        dashboard=dashboard_data,
    )


@admin_bp.get("/admin/products")
def products():
    products_data = list_admin_products()
    return render_template(
        "admin/products/index.html",
        page_title="Admin Products",
        products=products_data,
    )


@admin_bp.route("/admin/products/new", methods=["GET", "POST"])
def product_create():
    categories = list_admin_categories()
    form_data = get_product_form_defaults()
    errors = {}

    if request.method == "POST":
        form_data = extract_product_form_data(request.form)
        validated_data, errors = validate_product_form_data(
            form_data,
            image_file=request.files.get("image_file"),
        )

        if validated_data.get("slug"):
            form_data["slug"] = validated_data["slug"]

        if not errors:
            product = create_product(validated_data, request.files.get("image_file"))
            flash(f"{product.name} has been created.", "success")
            return redirect_to_next("admin.product_detail", product_id=product.id)

    return render_template(
        "admin/products/form.html",
        page_title="Create Product",
        product=None,
        mode="create",
        form_data=form_data,
        errors=errors,
        categories=categories,
    )


@admin_bp.get("/admin/products/<int:product_id>")
def product_detail(product_id):
    product = get_admin_product(product_id)
    if product is None:
        return render_template(
            "admin/products/not_found.html",
            page_title="Product Not Found",
            missing_product_id=product_id,
        ), 404

    return render_template(
        "admin/products/detail.html",
        page_title=product.name,
        product=product,
    )


@admin_bp.route("/admin/products/<int:product_id>/edit", methods=["GET", "POST"])
def product_edit(product_id):
    product = get_admin_product(product_id)
    if product is None:
        return render_template(
            "admin/products/not_found.html",
            page_title="Product Not Found",
            missing_product_id=product_id,
        ), 404

    categories = list_admin_categories()
    form_data = get_product_form_defaults(product)
    errors = {}

    if request.method == "POST":
        form_data = extract_product_form_data(request.form)
        validated_data, errors = validate_product_form_data(
            form_data,
            image_file=request.files.get("image_file"),
            existing_product=product,
        )

        if validated_data.get("slug"):
            form_data["slug"] = validated_data["slug"]

        if not errors:
            product = update_product(product, validated_data, request.files.get("image_file"))
            flash(f"{product.name} has been updated.", "success")
            return redirect_to_next("admin.product_detail", product_id=product.id)

    return render_template(
        "admin/products/form.html",
        page_title=f"Edit {product.name}",
        product=product,
        mode="edit",
        form_data=form_data,
        errors=errors,
        categories=categories,
    )


@admin_bp.post("/admin/products/<int:product_id>/toggle-status")
def product_toggle_status(product_id):
    product = get_admin_product(product_id)
    if product is None:
        return render_template(
            "admin/products/not_found.html",
            page_title="Product Not Found",
            missing_product_id=product_id,
        ), 404

    is_active = toggle_product_active(product)
    if is_active:
        flash(f"{product.name} is active again.", "success")
    else:
        flash(f"{product.name} has been deactivated.", "success")

    return redirect_to_next("admin.product_detail", product_id=product.id)


@admin_bp.get("/admin/categories")
def categories():
    category_rows = list_admin_category_rows()
    return render_template(
        "admin/categories/index.html",
        page_title="Admin Categories",
        category_rows=category_rows,
    )


@admin_bp.route("/admin/categories/new", methods=["GET", "POST"])
def category_create():
    form_data = get_category_form_defaults()
    errors = {}

    if request.method == "POST":
        form_data = extract_category_form_data(request.form)
        validated_data, errors = validate_category_form_data(form_data)

        if validated_data.get("slug"):
            form_data["slug"] = validated_data["slug"]

        if not errors:
            category = create_category(validated_data)
            flash(f"{category.name} has been created.", "success")
            return redirect_to_next("admin.categories")

    return render_template(
        "admin/categories/form.html",
        page_title="Create Category",
        category=None,
        mode="create",
        form_data=form_data,
        errors=errors,
        usage_count=0,
    )


@admin_bp.route("/admin/categories/<int:category_id>/edit", methods=["GET", "POST"])
def category_edit(category_id):
    category = get_admin_category(category_id)
    if category is None:
        return render_template(
            "admin/categories/not_found.html",
            page_title="Category Not Found",
            missing_category_id=category_id,
        ), 404

    form_data = get_category_form_defaults(category)
    errors = {}
    usage_count = get_category_usage_count(category.id)

    if request.method == "POST":
        form_data = extract_category_form_data(request.form)
        validated_data, errors = validate_category_form_data(
            form_data,
            existing_category=category,
        )

        if validated_data.get("slug"):
            form_data["slug"] = validated_data["slug"]

        if not errors:
            category = update_category(category, validated_data)
            flash(f"{category.name} has been updated.", "success")
            return redirect_to_next("admin.categories")

    return render_template(
        "admin/categories/form.html",
        page_title=f"Edit {category.name}",
        category=category,
        mode="edit",
        form_data=form_data,
        errors=errors,
        usage_count=usage_count,
    )


@admin_bp.get("/admin/orders")
def orders():
    orders_data = list_admin_orders()
    return render_template(
        "admin/orders/index.html",
        page_title="Admin Orders",
        orders=orders_data,
    )


@admin_bp.get("/admin/orders/<order_number>")
def order_detail(order_number):
    order = get_admin_order(order_number)
    if order is None:
        return render_template(
            "admin/orders/not_found.html",
            page_title="Order Not Found",
            missing_order_number=order_number,
        ), 404

    return render_template(
        "admin/orders/detail.html",
        page_title=order.order_number,
        order=order,
        order_status_choices=get_order_status_choices(order),
        payment_status_choices=get_payment_status_choices(),
    )


@admin_bp.post("/admin/orders/<order_number>/status")
def order_update_status(order_number):
    order = get_admin_order(order_number)
    if order is None:
        return render_template(
            "admin/orders/not_found.html",
            page_title="Order Not Found",
            missing_order_number=order_number,
        ), 404

    new_status = request.form.get("order_status", "").strip()

    try:
        update_admin_order_status(order, new_status)
    except ValueError as exc:
        flash(str(exc), "error")
    else:
        flash(f"Order {order.order_number} updated to {order.order_status}.", "success")

    return redirect_to_next("admin.order_detail", order_number=order.order_number)


@admin_bp.post("/admin/orders/<order_number>/payment-status")
def order_update_payment_status(order_number):
    order = get_admin_order(order_number)
    if order is None:
        return render_template(
            "admin/orders/not_found.html",
            page_title="Order Not Found",
            missing_order_number=order_number,
        ), 404

    new_status = request.form.get("payment_status", "").strip()

    try:
        update_admin_payment_status(order, new_status)
    except ValueError as exc:
        flash(str(exc), "error")
    else:
        flash(
            f"Payment status for {order.order_number} updated to {order.payment_status}.",
            "success",
        )

    return redirect_to_next("admin.order_detail", order_number=order.order_number)


@admin_bp.get("/admin/users")
def users():
    return render_template(
        "admin/section_placeholder.html",
        page_title="Admin Users",
        section_title="Users",
        section_copy="Reference the current demo account roles and the admin navigation structure.",
    )
