from decimal import Decimal
from datetime import datetime

from werkzeug.security import generate_password_hash

from ..extensions import db
from ..models import Category, Order, OrderItem, Product, User

SEEDED_USERS = [
    {
        "name": "GAINZ LAB Admin",
        "email": "admin@gainzlab.local",
        "password": "Admin123!",
        "role": "admin",
    },
    {
        "name": "Sample Customer",
        "email": "customer@gainzlab.local",
        "password": "Customer123!",
        "role": "customer",
    },
]

CATEGORY_DATA = [
    {
        "name": "Protein",
        "slug": "protein",
        "description": "Premium protein powders and blends formulated to support performance, recovery, and consistent daily intake.",
    },
    {
        "name": "Pre-Workout",
        "slug": "pre-workout",
        "description": "Training formulas built to support focus, energy, and high-effort sessions.",
    },
    {
        "name": "Creatine",
        "slug": "creatine",
        "description": "Creatine products designed to support power output, strength routines, and performance consistency.",
    },
    {
        "name": "Recovery",
        "slug": "recovery",
        "description": "Hydration and post-workout support products for demanding training schedules.",
    },
    {
        "name": "Bundles",
        "slug": "bundles",
        "description": "Convenient product stacks for customers building a complete training-day routine.",
    },
    {
        "name": "Accessories",
        "slug": "accessories",
        "description": "Daily-use training and mixing essentials that support a cleaner supplement workflow.",
    },
]

PRODUCT_DATA = [
    {
        "category_slug": "protein",
        "name": "GAINZ LAB Whey Core",
        "slug": "gainz-lab-whey-core",
        "short_description": "Premium whey protein blend formulated to support strength goals and post-training recovery.",
        "full_description": "GAINZ LAB Whey Core delivers a clean, easy-mixing protein option for athletes and lifters who want dependable daily nutrition. Built for training days and busy schedules, it supports muscle-building goals with a straightforward formula and no unnecessary filler focus.",
        "price": Decimal("1799.00"),
        "stock": 48,
        "flavor_or_variant": "Double Chocolate",
        "size_or_weight": "2 lb",
        "image_path": "img/products/gainz-lab-whey-core.jpg",
        "is_active": True,
    },
    {
        "category_slug": "protein",
        "name": "GAINZ LAB Iso Lean",
        "slug": "gainz-lab-iso-lean",
        "short_description": "Light and smooth protein option crafted for lean daily intake and consistent recovery support.",
        "full_description": "GAINZ LAB Iso Lean is a refined protein choice for customers who want a cleaner texture and a lighter finish after training. It is positioned as a convenient everyday formula that supports protein intake, recovery routines, and overall performance-focused nutrition.",
        "price": Decimal("2199.00"),
        "stock": 32,
        "flavor_or_variant": "Vanilla Frost",
        "size_or_weight": "2 lb",
        "image_path": "img/products/gainz-lab-iso-lean.jpg",
        "is_active": True,
    },
    {
        "category_slug": "pre-workout",
        "name": "GAINZ LAB Pre-Ignite",
        "slug": "gainz-lab-pre-ignite",
        "short_description": "High-impact pre-workout formulated to support training intensity, focus, and gym readiness.",
        "full_description": "GAINZ LAB Pre-Ignite is built for customers who want a sharper start before demanding sessions. The formula is positioned to support energy, focus, and performance output while keeping the product language clean and student-project friendly.",
        "price": Decimal("1399.00"),
        "stock": 40,
        "flavor_or_variant": "Blue Razz",
        "size_or_weight": "30 servings",
        "image_path": "img/products/gainz-lab-pre-ignite.jpg",
        "is_active": True,
    },
    {
        "category_slug": "pre-workout",
        "name": "GAINZ LAB Pump Drive",
        "slug": "gainz-lab-pump-drive",
        "short_description": "Performance pre-workout crafted to support focus and hard-training momentum.",
        "full_description": "GAINZ LAB Pump Drive is a pre-session formula for customers who want purposeful support before compound lifts, accessory work, or conditioning blocks. It is framed as a training companion that supports effort, concentration, and routine consistency.",
        "price": Decimal("1299.00"),
        "stock": 26,
        "flavor_or_variant": "Fruit Burst",
        "size_or_weight": "25 servings",
        "image_path": "img/products/gainz-lab-pump-drive.jpg",
        "is_active": True,
    },
    {
        "category_slug": "creatine",
        "name": "GAINZ LAB Creatine Monohydrate",
        "slug": "gainz-lab-creatine-monohydrate",
        "short_description": "Classic unflavored creatine support for strength, power, and repeatable gym performance.",
        "full_description": "GAINZ LAB Creatine Monohydrate keeps the formula simple and recognizable for customers who want an easy daily add-on. It is positioned to support strength work, repeated high-effort output, and long-term training consistency.",
        "price": Decimal("899.00"),
        "stock": 65,
        "flavor_or_variant": "Unflavored",
        "size_or_weight": "300 g",
        "image_path": "img/products/gainz-lab-creatine-monohydrate.jpg",
        "is_active": True,
    },
    {
        "category_slug": "recovery",
        "name": "GAINZ LAB Recover+",
        "slug": "gainz-lab-recover-plus",
        "short_description": "Recovery blend designed to support post-workout replenishment and next-session readiness.",
        "full_description": "GAINZ LAB Recover+ is aimed at athletes and everyday grinders who want a dedicated post-training option in their routine. The product messaging focuses on supporting recovery, replenishment, and consistency across heavy training weeks.",
        "price": Decimal("1249.00"),
        "stock": 28,
        "flavor_or_variant": "Citrus Punch",
        "size_or_weight": "20 servings",
        "image_path": "img/products/gainz-lab-recover-plus.jpg",
        "is_active": True,
    },
    {
        "category_slug": "recovery",
        "name": "GAINZ LAB Hydrate Reset",
        "slug": "gainz-lab-hydrate-reset",
        "short_description": "Hydration support mix built for training days, travel days, and routine consistency.",
        "full_description": "GAINZ LAB Hydrate Reset is a practical recovery-category product built around convenience and repeat use. It is framed as a support product for hydration habits, post-session reset, and better day-to-day supplement discipline.",
        "price": Decimal("849.00"),
        "stock": 34,
        "flavor_or_variant": "Berry Lime",
        "size_or_weight": "15 stick packs",
        "image_path": "img/products/gainz-lab-hydrate-reset.jpg",
        "is_active": True,
    },
    {
        "category_slug": "bundles",
        "name": "GAINZ LAB Starter Stack",
        "slug": "gainz-lab-starter-stack",
        "short_description": "Beginner-friendly bundle that supports a simple and consistent supplement routine.",
        "full_description": "GAINZ LAB Starter Stack groups together foundational products for customers who want a cleaner entry point into performance nutrition. It is positioned as a value-focused bundle that supports routine-building without overcomplicating the lineup.",
        "price": Decimal("3299.00"),
        "stock": 18,
        "flavor_or_variant": "Chocolate + Blue Razz",
        "size_or_weight": "Bundle",
        "image_path": "img/products/gainz-lab-starter-stack.jpg",
        "is_active": True,
    },
    {
        "category_slug": "bundles",
        "name": "GAINZ LAB Strength Stack",
        "slug": "gainz-lab-strength-stack",
        "short_description": "Advanced bundle assembled for customers training with a strength-first focus.",
        "full_description": "GAINZ LAB Strength Stack is built as a more complete bundle for serious training blocks. The messaging centers on supporting strength work, performance output, and a disciplined supplement setup across demanding routines.",
        "price": Decimal("4199.00"),
        "stock": 12,
        "flavor_or_variant": "Unflavored + Fruit Burst",
        "size_or_weight": "Bundle",
        "image_path": "img/products/gainz-lab-strength-stack.jpg",
        "is_active": True,
    },
    {
        "category_slug": "accessories",
        "name": "GAINZ LAB Shaker Bottle",
        "slug": "gainz-lab-shaker-bottle",
        "short_description": "Durable shaker built for smooth mixing, daily carry, and gym-bag convenience.",
        "full_description": "GAINZ LAB Shaker Bottle is a simple accessory product designed to round out the storefront lineup. It supports daily supplement use with an easy-grip design and a clean branded look that fits the GAINZ LAB identity.",
        "price": Decimal("399.00"),
        "stock": 90,
        "flavor_or_variant": "Smoke Black",
        "size_or_weight": "700 ml",
        "image_path": "img/products/gainz-lab-shaker-bottle.jpg",
        "is_active": True,
    },
    {
        "category_slug": "accessories",
        "name": "GAINZ LAB Resistance Band Set",
        "slug": "gainz-lab-resistance-band-set",
        "short_description": "Three-band training set that supports warm-ups, activation work, and home sessions.",
        "full_description": "GAINZ LAB Resistance Band Set expands the catalog with a practical accessory for mobility drills, activation work, and light resistance training. It is positioned as a useful add-on for customers who want extra flexibility in their routine.",
        "price": Decimal("699.00"),
        "stock": 44,
        "flavor_or_variant": "Light / Medium / Heavy",
        "size_or_weight": "3-piece set",
        "image_path": "img/products/gainz-lab-resistance-band-set.jpg",
        "is_active": True,
    },
]

ORDER_DATA = [
    {
        "order_number": "GL-DEMO-1001",
        "user_email": "customer@gainzlab.local",
        "shipping_method": "Standard Delivery",
        "payment_method": "Cash on Delivery",
        "payment_status": "Pending",
        "order_status": "Pending",
        "delivery_address": "214 Performance Ave, Quezon City, Metro Manila",
        "contact_number": "+63 917 555 0148",
        "placed_at": datetime(2026, 3, 18, 9, 15),
        "items": [
            {"product_slug": "gainz-lab-whey-core", "quantity": 1},
            {"product_slug": "gainz-lab-creatine-monohydrate", "quantity": 1},
        ],
    },
    {
        "order_number": "GL-DEMO-1002",
        "user_email": "customer@gainzlab.local",
        "shipping_method": "Express Delivery",
        "payment_method": "Simulated GCash",
        "payment_status": "Paid",
        "order_status": "Shipped",
        "delivery_address": "88 Athlete Street, Pasig City, Metro Manila",
        "contact_number": "+63 918 444 2200",
        "placed_at": datetime(2026, 3, 17, 14, 30),
        "items": [
            {"product_slug": "gainz-lab-pre-ignite", "quantity": 1},
            {"product_slug": "gainz-lab-recover-plus", "quantity": 1},
            {"product_slug": "gainz-lab-shaker-bottle", "quantity": 1},
        ],
    },
    {
        "order_number": "GL-DEMO-1003",
        "user_email": "customer@gainzlab.local",
        "shipping_method": "Store Pickup",
        "payment_method": "Simulated Card",
        "payment_status": "Paid",
        "order_status": "Delivered",
        "delivery_address": "GAINZ LAB Demo Pickup Desk, Makati City",
        "contact_number": "+63 917 321 5566",
        "placed_at": datetime(2026, 3, 15, 11, 0),
        "items": [
            {"product_slug": "gainz-lab-strength-stack", "quantity": 1},
            {"product_slug": "gainz-lab-resistance-band-set", "quantity": 1},
        ],
    },
]

SHIPPING_FEES = {
    "Standard Delivery": Decimal("99.00"),
    "Express Delivery": Decimal("199.00"),
    "Store Pickup": Decimal("0.00"),
}


def seed_sample_data():
    users = [_upsert_user(item) for item in SEEDED_USERS]
    categories = [_upsert_category(item) for item in CATEGORY_DATA]

    db.session.flush()

    user_by_email = {user.email: user for user in users}
    category_by_slug = {category.slug: category for category in categories}
    products = [_upsert_product(item, category_by_slug) for item in PRODUCT_DATA]
    db.session.flush()
    product_by_slug = {product.slug: product for product in products}
    orders = [_upsert_order(item, user_by_email, product_by_slug) for item in ORDER_DATA]

    db.session.commit()

    return {
        "users": users,
        "categories": categories,
        "products": products,
        "orders": orders,
    }


def _upsert_user(payload):
    user = User.query.filter_by(email=payload["email"]).one_or_none()
    if user is None:
        user = User(email=payload["email"])
        db.session.add(user)

    user.name = payload["name"]
    user.role = payload["role"]
    user.password_hash = generate_password_hash(payload["password"])
    return user


def _upsert_category(payload):
    category = Category.query.filter_by(slug=payload["slug"]).one_or_none()
    if category is None:
        category = Category(slug=payload["slug"])
        db.session.add(category)

    category.name = payload["name"]
    category.description = payload["description"]
    return category


def _upsert_product(payload, category_by_slug):
    product = Product.query.filter_by(slug=payload["slug"]).one_or_none()
    if product is None:
        product = Product(slug=payload["slug"])
        db.session.add(product)

    product.category = category_by_slug[payload["category_slug"]]
    product.name = payload["name"]
    product.short_description = payload["short_description"]
    product.full_description = payload["full_description"]
    product.price = payload["price"]
    product.stock = payload["stock"]
    product.flavor_or_variant = payload["flavor_or_variant"]
    product.size_or_weight = payload["size_or_weight"]
    product.image_path = payload["image_path"]
    product.is_active = payload["is_active"]
    return product


def _upsert_order(payload, user_by_email, product_by_slug):
    order = Order.query.filter_by(order_number=payload["order_number"]).one_or_none()
    if order is None:
        order = Order(order_number=payload["order_number"])
        db.session.add(order)

    order.user = user_by_email[payload["user_email"]]
    order.shipping_method = payload["shipping_method"]
    order.payment_method = payload["payment_method"]
    order.payment_status = payload["payment_status"]
    order.order_status = payload["order_status"]
    order.delivery_address = payload["delivery_address"]
    order.contact_number = payload["contact_number"]
    order.placed_at = payload["placed_at"]
    order.created_at = payload["placed_at"]
    order.updated_at = payload["placed_at"]

    existing_items = list(order.items)
    for item in existing_items:
        db.session.delete(item)

    subtotal = Decimal("0.00")
    order_items = []

    for item_payload in payload["items"]:
        product = product_by_slug[item_payload["product_slug"]]
        quantity = item_payload["quantity"]
        line_total = product.price * quantity
        subtotal += line_total
        order_items.append(
            OrderItem(
                order=order,
                product=product,
                product_name_snapshot=product.name,
                price_snapshot=product.price,
                quantity=quantity,
                line_total=line_total,
                created_at=payload["placed_at"],
                updated_at=payload["placed_at"],
            )
        )

    order.subtotal = subtotal
    order.shipping_fee = SHIPPING_FEES[payload["shipping_method"]]
    order.total_amount = subtotal + order.shipping_fee

    db.session.add_all(order_items)
    return order
