# GAINZ LAB

GAINZ LAB is a student final-project e-commerce website for a fitness supplement brand. It includes a customer storefront, cart and checkout flow, order history, and an admin area for managing products, categories, and orders.

This is an academic/demo project. Product content is for presentation purposes only and does not provide medical advice.

## Live Demo
After deployment, place your live URL here so visitors can open the site directly from GitHub:

`Live Demo: https://your-render-url.onrender.com`

## Features
- Customer registration, login, and logout
- Role-based access for `customer` and `admin`
- Product catalog with category filtering and product-name search
- Product details page with quantity selection and related products
- Shopping cart with add, update, remove, and subtotal
- Checkout with delivery address, contact number, shipping method, and simulated payment method
- Order confirmation and customer order history
- Admin dashboard with summary cards, recent orders, and low-stock overview
- Admin product management
- Admin category management
- Admin order management

## Tech Stack
- Flask
- Flask-SQLAlchemy / SQLAlchemy
- Flask-Login
- SQLite
- python-dotenv
- Jinja templates, HTML, CSS, minimal JavaScript

## Setup
From the project root:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env -ErrorAction SilentlyContinue
.venv\Scripts\flask.exe --app run.py init-db
.venv\Scripts\flask.exe --app run.py seed-db
.venv\Scripts\python.exe run.py
```

Open the app at [http://127.0.0.1:5000](http://127.0.0.1:5000).

## Render Deployment
This repository includes [render.yaml](render.yaml) for a basic Render web-service deployment.

1. Push the latest code to GitHub.
2. In Render, create a new web service from this repository.
3. Render should detect the existing `render.yaml` settings.
4. After the first deploy, open the generated `onrender.com` URL.

This deployment starts by running:
- `flask --app run.py init-db`
- `flask --app run.py seed-db`
- `gunicorn --bind 0.0.0.0:$PORT run:app`

That means the demo database, demo accounts, and sample catalog/order data are recreated automatically on service boot for a stable presentation flow.

## Demo Accounts
- Admin: `admin@gainzlab.local` / `Admin123!`
- Customer: `customer@gainzlab.local` / `Customer123!`

The seed command also loads sample categories, products, and demo orders for presentation.

## Group Members
- Jerico Miguel A. Lindain
- Christian James T. Able
- Roeb Andrei L. Dela Cruz
- Vince Lander G. Leander
- Luis Miguel A. Mina

## Main Modules
- Home
- Categories
- Shop
- Product Details
- Cart
- Checkout
- Order History
- Profile
- Admin Dashboard
- Admin Products
- Admin Categories
- Admin Orders

## Database Summary
Main tables:
- `users`
- `categories`
- `products`
- `cart_items`
- `orders`
- `order_items`

Core relationships:
- one category has many products
- one user has many cart items
- one user has many orders
- one order has many order items

## Security Measures Implemented
- Password hashing
- Login-required customer routes
- Admin-only route protection
- Input validation for auth, cart, checkout, and admin forms
- Safe redirect handling for login redirects
- SQLite foreign-key enforcement
- Session cookie settings for `HttpOnly` and `SameSite=Lax`

## Limitations
- CSRF protection is not implemented yet
- Payment is simulated only
- Shipping fees are implemented, but estimated delivery time is not shown yet
- Admin user management is still a placeholder
- Product deletion uses soft deactivation instead of destructive delete
- The Render demo deployment uses SQLite and auto-seeded demo data, so it is suitable for presentation use, not production use

## Testing
Run:

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Demo Flow
`Home -> Shop -> Product Details -> Cart -> Checkout -> Order History -> Admin Dashboard -> Product Management -> Order Management`

## Documentation
For a slightly more detailed project summary, see [PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md).
