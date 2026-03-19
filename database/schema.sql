
CREATE TABLE categories (
	id INTEGER NOT NULL, 
	name VARCHAR(120) NOT NULL, 
	description TEXT, 
	slug VARCHAR(140) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_categories_name ON categories (name);

CREATE UNIQUE INDEX ix_categories_slug ON categories (slug);


CREATE TABLE users (
	id INTEGER NOT NULL, 
	name VARCHAR(120) NOT NULL, 
	email VARCHAR(255) NOT NULL, 
	password_hash VARCHAR(255) NOT NULL, 
	role VARCHAR(20) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_users_role CHECK (role IN ('customer', 'admin'))
);

CREATE UNIQUE INDEX ix_users_email ON users (email);

CREATE INDEX ix_users_role ON users (role);


CREATE TABLE orders (
	id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	order_number VARCHAR(40) NOT NULL, 
	subtotal NUMERIC(10, 2) NOT NULL, 
	shipping_fee NUMERIC(10, 2) NOT NULL, 
	total_amount NUMERIC(10, 2) NOT NULL, 
	shipping_method VARCHAR(40) NOT NULL, 
	payment_method VARCHAR(40) NOT NULL, 
	payment_status VARCHAR(20) NOT NULL, 
	order_status VARCHAR(20) NOT NULL, 
	delivery_address TEXT NOT NULL, 
	contact_number VARCHAR(30) NOT NULL, 
	placed_at DATETIME NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_orders_subtotal_non_negative CHECK (subtotal >= 0), 
	CONSTRAINT ck_orders_shipping_fee_non_negative CHECK (shipping_fee >= 0), 
	CONSTRAINT ck_orders_total_amount_non_negative CHECK (total_amount >= 0), 
	CONSTRAINT ck_orders_shipping_method CHECK (shipping_method IN ('Standard Delivery', 'Express Delivery', 'Store Pickup')), 
	CONSTRAINT ck_orders_payment_method CHECK (payment_method IN ('Cash on Delivery', 'Simulated GCash', 'Simulated Card')), 
	CONSTRAINT ck_orders_payment_status CHECK (payment_status IN ('Pending', 'Paid', 'Failed', 'Cancelled')), 
	CONSTRAINT ck_orders_order_status CHECK (order_status IN ('Pending', 'Confirmed', 'Shipped', 'Delivered', 'Cancelled')), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE RESTRICT
);

CREATE UNIQUE INDEX ix_orders_order_number ON orders (order_number);

CREATE INDEX ix_orders_order_status ON orders (order_status);

CREATE INDEX ix_orders_placed_at ON orders (placed_at);

CREATE INDEX ix_orders_user_id ON orders (user_id);

CREATE INDEX ix_orders_user_status ON orders (user_id, order_status);


CREATE TABLE products (
	id INTEGER NOT NULL, 
	category_id INTEGER NOT NULL, 
	name VARCHAR(160) NOT NULL, 
	slug VARCHAR(180) NOT NULL, 
	short_description VARCHAR(255) NOT NULL, 
	full_description TEXT NOT NULL, 
	price NUMERIC(10, 2) NOT NULL, 
	stock INTEGER NOT NULL, 
	flavor_or_variant VARCHAR(120), 
	size_or_weight VARCHAR(120), 
	image_path VARCHAR(255), 
	is_active BOOLEAN NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_products_price_non_negative CHECK (price >= 0), 
	CONSTRAINT ck_products_stock_non_negative CHECK (stock >= 0), 
	FOREIGN KEY(category_id) REFERENCES categories (id) ON DELETE RESTRICT
);

CREATE INDEX ix_products_category_active ON products (category_id, is_active);

CREATE INDEX ix_products_category_id ON products (category_id);

CREATE INDEX ix_products_is_active ON products (is_active);

CREATE INDEX ix_products_name ON products (name);

CREATE UNIQUE INDEX ix_products_slug ON products (slug);


CREATE TABLE cart_items (
	id INTEGER NOT NULL, 
	user_id INTEGER NOT NULL, 
	product_id INTEGER NOT NULL, 
	quantity INTEGER NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_cart_items_user_product UNIQUE (user_id, product_id), 
	CONSTRAINT ck_cart_items_quantity_positive CHECK (quantity > 0), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(product_id) REFERENCES products (id) ON DELETE CASCADE
);

CREATE INDEX ix_cart_items_product_id ON cart_items (product_id);

CREATE INDEX ix_cart_items_user_created ON cart_items (user_id, created_at);

CREATE INDEX ix_cart_items_user_id ON cart_items (user_id);


CREATE TABLE order_items (
	id INTEGER NOT NULL, 
	order_id INTEGER NOT NULL, 
	product_id INTEGER, 
	product_name_snapshot VARCHAR(160) NOT NULL, 
	price_snapshot NUMERIC(10, 2) NOT NULL, 
	quantity INTEGER NOT NULL, 
	line_total NUMERIC(10, 2) NOT NULL, 
	created_at DATETIME NOT NULL, 
	updated_at DATETIME NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_order_items_price_snapshot_non_negative CHECK (price_snapshot >= 0), 
	CONSTRAINT ck_order_items_quantity_positive CHECK (quantity > 0), 
	CONSTRAINT ck_order_items_line_total_non_negative CHECK (line_total >= 0), 
	FOREIGN KEY(order_id) REFERENCES orders (id) ON DELETE CASCADE, 
	FOREIGN KEY(product_id) REFERENCES products (id) ON DELETE SET NULL
);

CREATE INDEX ix_order_items_order_id ON order_items (order_id);

CREATE INDEX ix_order_items_order_product ON order_items (order_id, product_id);

CREATE INDEX ix_order_items_product_id ON order_items (product_id);
