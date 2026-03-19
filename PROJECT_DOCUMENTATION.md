# GAINZ LAB Project Documentation

## Project Overview
GAINZ LAB is a student final-project e-commerce website for a fitness supplement brand. The project presents a modern online store experience where customers can browse products, manage a cart, place simulated orders, and review their purchase history. It also includes an admin side for managing products, categories, and order status updates.

This project is an academic/demo build. Product content is written for presentation purposes and avoids medical or disease-treatment claims.

## Main Features
- Customer registration, login, and logout
- Role-based access for `customer` and `admin`
- Product catalog with category filtering and product-name search
- Product details page with quantity selection and related products
- Shopping cart with add, update, remove, and subtotal
- Checkout with delivery address, contact number, shipping method, and simulated payment method
- Order placement, confirmation page, and customer order history
- Admin dashboard with summary cards, recent orders, and low-stock overview
- Admin product management with create, edit, view, and activate/deactivate
- Admin category management with usage counts
- Admin order management with status and payment-status updates

## Tech Stack Used
- Backend: Flask
- Database: SQLite
- ORM: Flask-SQLAlchemy / SQLAlchemy
- Authentication: Flask-Login
- Environment configuration: python-dotenv
- Frontend: Jinja templates, HTML, CSS, minimal JavaScript

## Setup Instructions
From the project root:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env -ErrorAction SilentlyContinue
.venv\Scripts\flask.exe --app run.py init-db
.venv\Scripts\flask.exe --app run.py seed-db
.venv\Scripts\python.exe run.py
```

Open the app at `http://127.0.0.1:5000`.

Optional test run:

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Demo Accounts
- Admin: `admin@gainzlab.local` / `Admin123!`
- Customer: `customer@gainzlab.local` / `Customer123!`

The seed data also includes sample categories, products, and demo orders for presentation.

## Database Summary
The application uses six main tables:

- `users`: stores account information, password hashes, and roles
- `categories`: stores product categories and category metadata
- `products`: stores product details, pricing, stock, and active status
- `cart_items`: stores the current cart contents for each logged-in customer
- `orders`: stores placed orders, totals, shipping/payment choices, and statuses
- `order_items`: stores item snapshots for each order

Foreign keys and model relationships connect:
- one category to many products
- one user to many cart items
- one user to many orders
- one order to many order items

## User Roles
- `Customer`
  - register and log in
  - browse products
  - manage cart
  - place orders
  - view personal order history
- `Admin`
  - access admin dashboard
  - manage products
  - manage categories
  - view all orders
  - update order and payment statuses

## Major Pages and Modules
- Home
- Categories
- Shop
- Product Details
- Login
- Register
- Profile
- Cart
- Checkout
- Order Confirmation
- Order History
- Admin Dashboard
- Admin Products
- Admin Categories
- Admin Orders

## Security Measures Implemented
- Password hashing using Werkzeug security helpers
- Login-required protection for customer account, cart, checkout, and order pages
- Admin-only protection for admin routes
- Input validation on registration, login, cart actions, checkout, and admin forms
- Safe redirect handling for login `next` URLs
- SQLite foreign-key enforcement
- Session cookie settings for `HttpOnly` and `SameSite=Lax`

## Limitations and Future Improvements
- CSRF protection is not implemented yet
- Payment flow is simulated only; there is no real payment gateway
- Shipping options include fees, but estimated delivery time is not shown yet
- Admin user management is still a placeholder page
- Product removal uses soft deactivation instead of destructive deletion
- Product reviews, ratings, and wishlist features are not implemented
- More automated tests and deployment configuration can still be added

## Presentation Notes
Recommended demo path:

`Home -> Shop -> Product Details -> Cart -> Checkout -> Order History -> Admin Dashboard -> Product Management -> Order Management`

This flow highlights both the customer experience and the admin management side in one presentation.
