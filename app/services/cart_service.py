from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import joinedload

from ..extensions import db
from ..models import CartItem, Product


@dataclass(frozen=True)
class CartLine:
    item: CartItem
    unit_price: Decimal
    line_total: Decimal


@dataclass(frozen=True)
class CartSnapshot:
    lines: list[CartLine]
    subtotal: Decimal
    total_quantity: int
    cart_ready: bool = True

    @property
    def is_empty(self):
        return not self.lines


def get_cart_snapshot(user_id):
    try:
        stmt = (
            select(CartItem)
            .options(
                joinedload(CartItem.product).joinedload(Product.category),
            )
            .where(CartItem.user_id == user_id)
            .order_by(CartItem.created_at.desc(), CartItem.id.desc())
        )
        items = db.session.execute(stmt).scalars().all()
    except OperationalError:
        return CartSnapshot(
            lines=[],
            subtotal=Decimal("0.00"),
            total_quantity=0,
            cart_ready=False,
        )

    lines = []
    subtotal = Decimal("0.00")
    total_quantity = 0

    for item in items:
        unit_price = item.product.price
        line_total = unit_price * item.quantity
        subtotal += line_total
        total_quantity += item.quantity
        lines.append(
            CartLine(
                item=item,
                unit_price=unit_price,
                line_total=line_total,
            )
        )

    return CartSnapshot(
        lines=lines,
        subtotal=subtotal,
        total_quantity=total_quantity,
        cart_ready=True,
    )


def add_product_to_cart(user_id, product_id, quantity):
    product = _get_active_product(product_id)
    if product is None:
        raise LookupError

    requested_quantity = _validate_quantity(quantity)

    item = CartItem.query.filter_by(user_id=user_id, product_id=product.id).one_or_none()
    new_quantity = requested_quantity

    if item is not None:
        new_quantity = item.quantity + requested_quantity

    _validate_stock(product, new_quantity)

    if item is None:
        item = CartItem(
            user_id=user_id,
            product_id=product.id,
            quantity=requested_quantity,
        )
        db.session.add(item)
    else:
        item.quantity = new_quantity

    db.session.commit()

    return f"Added {requested_quantity} x {product.name} to your cart."


def update_cart_item_quantity(user_id, item_id, quantity):
    item = _get_cart_item(user_id, item_id)
    if item is None:
        raise LookupError

    if not item.product.is_active:
        raise ValueError("This product is no longer available. Remove it from your cart.")

    new_quantity = _validate_quantity(quantity)
    _validate_stock(item.product, new_quantity)

    item.quantity = new_quantity
    db.session.commit()
    return f"Updated {item.product.name} to {new_quantity} in your cart."


def remove_cart_item(user_id, item_id):
    item = _get_cart_item(user_id, item_id)
    if item is None:
        raise LookupError

    product_name = item.product.name
    db.session.delete(item)
    db.session.commit()
    return f"Removed {product_name} from your cart."


def _get_active_product(product_id):
    product = db.session.get(Product, product_id)
    if product is None or not product.is_active:
        return None

    return product


def _get_cart_item(user_id, item_id):
    stmt = (
        select(CartItem)
        .options(
            joinedload(CartItem.product).joinedload(Product.category),
        )
        .where(
            CartItem.id == item_id,
            CartItem.user_id == user_id,
        )
    )
    return db.session.execute(stmt).scalar_one_or_none()


def _validate_quantity(quantity):
    if quantity is None or quantity < 1:
        raise ValueError("Choose a quantity of at least 1.")

    return quantity


def _validate_stock(product, quantity):
    if product.stock < 1:
        raise ValueError("This product is currently out of stock.")

    if quantity > product.stock:
        raise ValueError(f"Only {product.stock} units of {product.name} are available.")
