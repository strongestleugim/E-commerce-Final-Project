from .account import account_bp
from .admin import admin_bp
from .auth import auth_bp
from .cart import cart_bp
from .checkout import checkout_bp
from .main import main_bp
from .orders import orders_bp
from .shop import shop_bp

BLUEPRINTS = [
    main_bp,
    shop_bp,
    cart_bp,
    checkout_bp,
    auth_bp,
    account_bp,
    orders_bp,
    admin_bp,
]

