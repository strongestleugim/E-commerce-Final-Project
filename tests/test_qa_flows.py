import tempfile
import unittest
from pathlib import Path

from app import create_app
from app.extensions import db
from app.models import CartItem, Order, Product, User
from app.services.seed_service import seed_sample_data


class TestConfig:
    TESTING = True
    SECRET_KEY = "test-secret-key"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    BRAND_NAME = "GAINZ LAB"
    BRAND_TAGLINE = "Engineered Results"
    BRAND_CONTACT = {
        "email": "support@gainzlab.local",
        "phone": "+63 917 555 0148",
        "location": "Metro Manila Demo Fulfillment",
    }
    PREFERRED_CATEGORIES = []
    DEMO_DISCLAIMER = "This is a test instance."


class QAFlowTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="gainzlab-tests-"))
        self.upload_dir = self.temp_dir / "uploads"
        self.db_path = self.temp_dir / "test.db"

        config = type(
            "TestingConfig",
            (TestConfig,),
            {
                "SQLALCHEMY_DATABASE_URI": f"sqlite:///{self.db_path.as_posix()}",
                "PRODUCT_IMAGE_UPLOAD_DIR": str(self.upload_dir),
                "PRODUCT_IMAGE_UPLOAD_WEB_PATH": "img/products/uploads",
            },
        )

        self.app = create_app(config)
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()
        seed_sample_data()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def login(self, email, password):
        return self.client.post(
            "/login",
            data={"email": email, "password": password},
            follow_redirects=True,
        )

    def logout(self):
        return self.client.post("/logout", follow_redirects=True)

    def add_seed_product_to_cart(self, quantity="1"):
        product = Product.query.filter_by(slug="gainz-lab-whey-core").one()
        return self.client.post(
            "/cart/add",
            data={"product_id": product.id, "quantity": quantity, "next": "/cart"},
            follow_redirects=True,
        )

    def test_customer_registration_login_and_logout_work(self):
        response = self.client.post(
            "/register",
            data={
                "name": "QA Customer",
                "email": "qa@example.com",
                "password": "Password123!",
                "confirm_password": "Password123!",
            },
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Your customer account has been created.", response.get_data(as_text=True))

        logout_response = self.logout()
        self.assertEqual(logout_response.status_code, 200)
        self.assertIn("You have been logged out.", logout_response.get_data(as_text=True))

        login_response = self.login("qa@example.com", "Password123!")
        self.assertEqual(login_response.status_code, 200)
        self.assertIn("Welcome back, QA Customer.", login_response.get_data(as_text=True))

    def test_seed_data_includes_demo_accounts_and_orders(self):
        self.assertIsNotNone(User.query.filter_by(email="admin@gainzlab.local").one_or_none())
        self.assertIsNotNone(User.query.filter_by(email="customer@gainzlab.local").one_or_none())
        self.assertEqual(Order.query.count(), 3)

        self.login("customer@gainzlab.local", "Customer123!")
        orders_response = self.client.get("/orders")
        self.assertEqual(orders_response.status_code, 200)
        self.assertIn("GL-DEMO-1001", orders_response.get_data(as_text=True))
        self.logout()

        self.login("admin@gainzlab.local", "Admin123!")
        admin_response = self.client.get("/admin")
        self.assertEqual(admin_response.status_code, 200)
        self.assertIn("GL-DEMO-1001", admin_response.get_data(as_text=True))

    def test_shop_search_filter_and_product_view_are_public(self):
        self.assertEqual(self.client.get("/shop").status_code, 200)
        search_response = self.client.get("/shop?q=whey")
        self.assertEqual(search_response.status_code, 200)
        self.assertIn("GAINZ LAB Whey Core", search_response.get_data(as_text=True))

        filter_response = self.client.get("/shop?category=protein")
        self.assertEqual(filter_response.status_code, 200)
        self.assertIn("Protein", filter_response.get_data(as_text=True))

        detail_response = self.client.get("/products/gainz-lab-whey-core")
        self.assertEqual(detail_response.status_code, 200)
        self.assertIn("Add to Cart", detail_response.get_data(as_text=True))

    def test_cart_add_update_and_remove_flow_works_for_customer(self):
        self.login("customer@gainzlab.local", "Customer123!")
        add_response = self.add_seed_product_to_cart(quantity="2")
        self.assertIn("Added 2 x GAINZ LAB Whey Core to your cart.", add_response.get_data(as_text=True))

        item = CartItem.query.one()
        update_response = self.client.post(
            f"/cart/items/{item.id}/update",
            data={"quantity": "3", "next": "/cart"},
            follow_redirects=True,
        )
        self.assertEqual(update_response.status_code, 200)
        self.assertIn("Updated GAINZ LAB Whey Core to 3 in your cart.", update_response.get_data(as_text=True))

        remove_response = self.client.post(
            f"/cart/items/{item.id}/remove",
            data={"next": "/cart"},
            follow_redirects=True,
        )
        self.assertEqual(remove_response.status_code, 200)
        self.assertIn("Removed GAINZ LAB Whey Core from your cart.", remove_response.get_data(as_text=True))

    def test_checkout_requires_explicit_shipping_and_payment_selection(self):
        self.login("customer@gainzlab.local", "Customer123!")
        self.add_seed_product_to_cart()
        initial_order_count = Order.query.count()

        response = self.client.post(
            "/checkout",
            data={
                "delivery_address": "123 Demo Street, Manila",
                "contact_number": "+639123456789",
                "shipping_method": "",
                "payment_method": "",
            },
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        body = response.get_data(as_text=True)
        self.assertIn("Choose a shipping method.", body)
        self.assertIn("Choose a payment method.", body)
        self.assertEqual(Order.query.count(), initial_order_count)

    def test_checkout_creates_order_and_clears_cart(self):
        self.login("customer@gainzlab.local", "Customer123!")
        self.add_seed_product_to_cart(quantity="2")
        initial_order_count = Order.query.count()

        response = self.client.post(
            "/checkout",
            data={
                "delivery_address": "123 Demo Street, Manila",
                "contact_number": "+639123456789",
                "shipping_method": "Express Delivery",
                "payment_method": "Simulated GCash",
            },
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Order Confirmation", response.get_data(as_text=True))
        self.assertEqual(CartItem.query.count(), 0)
        self.assertEqual(Order.query.count(), initial_order_count + 1)

        order = Order.query.order_by(Order.id.desc()).first()
        self.assertEqual(order.shipping_method, "Express Delivery")
        self.assertEqual(order.payment_method, "Simulated GCash")
        self.assertEqual(order.payment_status, "Paid")
        self.assertEqual(len(order.items), 1)

    def test_customer_can_only_view_their_own_order_history(self):
        self.login("customer@gainzlab.local", "Customer123!")
        self.add_seed_product_to_cart()
        self.client.post(
            "/checkout",
            data={
                "delivery_address": "123 Demo Street, Manila",
                "contact_number": "+639123456789",
                "shipping_method": "Standard Delivery",
                "payment_method": "Cash on Delivery",
            },
            follow_redirects=True,
        )
        order = Order.query.order_by(Order.id.desc()).first()
        self.logout()

        self.client.post(
            "/register",
            data={
                "name": "Second Customer",
                "email": "second@example.com",
                "password": "Password123!",
                "confirm_password": "Password123!",
            },
            follow_redirects=True,
        )

        response = self.client.get(f"/orders/{order.order_number}")
        self.assertEqual(response.status_code, 404)

    def test_admin_can_manage_products_categories_and_orders(self):
        self.login("admin@gainzlab.local", "Admin123!")

        category_response = self.client.post(
            "/admin/categories/new",
            data={"name": "QA Category", "slug": "qa-category", "description": "Testing category."},
            follow_redirects=True,
        )
        self.assertEqual(category_response.status_code, 200)
        self.assertIn("QA Category has been created.", category_response.get_data(as_text=True))
        product_category = Product.query.filter_by(slug="gainz-lab-whey-core").one().category

        qa_category_edit = self.client.post(
            f"/admin/categories/{product_category.id}/edit",
            data={
                "name": "Protein Core",
                "slug": "protein",
                "description": "Updated category copy for QA coverage.",
            },
            follow_redirects=True,
        )
        self.assertEqual(qa_category_edit.status_code, 200)
        self.assertIn("Protein Core has been updated.", qa_category_edit.get_data(as_text=True))

        product_create = self.client.post(
            "/admin/products/new",
            data={
                "category_id": str(product_category.id),
                "name": "QA Product",
                "slug": "qa-product",
                "short_description": "Short description for QA product.",
                "full_description": "Full description for QA product that supports performance and routine consistency.",
                "price": "999.00",
                "stock": "6",
                "flavor_or_variant": "Test Flavor",
                "size_or_weight": "1 lb",
                "is_active": "on",
            },
            follow_redirects=True,
        )
        self.assertEqual(product_create.status_code, 200)
        self.assertIn("QA Product has been created.", product_create.get_data(as_text=True))
        qa_product = Product.query.filter_by(slug="qa-product").one()

        product_edit = self.client.post(
            f"/admin/products/{qa_product.id}/edit",
            data={
                "category_id": str(product_category.id),
                "name": "QA Product Updated",
                "slug": "qa-product",
                "short_description": "Updated short description for QA product.",
                "full_description": "Updated full description for QA product that supports performance and routine consistency.",
                "price": "1199.00",
                "stock": "4",
                "flavor_or_variant": "Updated Flavor",
                "size_or_weight": "2 lb",
                "is_active": "on",
            },
            follow_redirects=True,
        )
        self.assertEqual(product_edit.status_code, 200)
        self.assertIn("QA Product Updated has been updated.", product_edit.get_data(as_text=True))

        product_toggle = self.client.post(
            f"/admin/products/{qa_product.id}/toggle-status",
            data={"next": f"/admin/products/{qa_product.id}"},
            follow_redirects=True,
        )
        self.assertEqual(product_toggle.status_code, 200)
        self.assertIn("QA Product Updated has been deactivated.", product_toggle.get_data(as_text=True))

        self.logout()
        self.login("customer@gainzlab.local", "Customer123!")
        self.add_seed_product_to_cart()
        self.client.post(
            "/checkout",
            data={
                "delivery_address": "123 Demo Street, Manila",
                "contact_number": "+639123456789",
                "shipping_method": "Standard Delivery",
                "payment_method": "Cash on Delivery",
            },
            follow_redirects=True,
        )
        order = Order.query.order_by(Order.id.desc()).first()
        self.logout()

        self.login("admin@gainzlab.local", "Admin123!")
        order_response = self.client.post(
            f"/admin/orders/{order.order_number}/status",
            data={"order_status": "Confirmed", "next": f"/admin/orders/{order.order_number}"},
            follow_redirects=True,
        )
        self.assertEqual(order_response.status_code, 200)
        self.assertIn("updated to Confirmed", order_response.get_data(as_text=True))

    def test_admin_is_blocked_from_customer_cart_flow(self):
        self.login("admin@gainzlab.local", "Admin123!")
        product = Product.query.filter_by(slug="gainz-lab-whey-core").one()

        cart_page = self.client.get("/cart", follow_redirects=True)
        self.assertEqual(cart_page.status_code, 200)
        self.assertIn("/admin", cart_page.request.path)
        self.assertIn("Admin accounts cannot use the customer cart.", cart_page.get_data(as_text=True))

        add_response = self.client.post(
            "/cart/add",
            data={"product_id": product.id, "quantity": "1", "next": "/cart"},
            follow_redirects=True,
        )
        self.assertEqual(add_response.status_code, 200)
        self.assertIn("/admin", add_response.request.path)
        self.assertIn("Admin accounts cannot use the customer cart.", add_response.get_data(as_text=True))
        self.assertEqual(CartItem.query.count(), 0)

        product_page = self.client.get(f"/products/{product.slug}")
        self.assertEqual(product_page.status_code, 200)
        self.assertIn("Open Admin Dashboard", product_page.get_data(as_text=True))
        self.assertNotIn("Log In to Add to Cart", product_page.get_data(as_text=True))

    def test_customers_are_redirected_away_from_admin_routes(self):
        self.login("customer@gainzlab.local", "Customer123!")
        response = self.client.get("/admin", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.path, "/")
        self.assertIn("do not have permission", response.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
