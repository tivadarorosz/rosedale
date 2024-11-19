-- Drop tables if they exist
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS order_line_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS items;
DROP TABLE IF EXISTS agents;
DROP TABLE IF EXISTS locations;

-- Create customers table
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    latepoint_id INT UNIQUE,
    square_id TEXT UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    gender VARCHAR(10),
    dob DATE,
    location VARCHAR(100),
    postcode VARCHAR(10),
    status VARCHAR(20) NOT NULL CHECK (status IN ('active', 'deleted', 'vip')),
    type VARCHAR(20) NOT NULL DEFAULT 'client' CHECK (type IN ('client', 'employee')),
    source VARCHAR(20) NOT NULL CHECK (source IN ('admin', 'latepoint', 'square', 'acuity')),
    is_pregnant BOOLEAN,
    has_cancer BOOLEAN,
    has_blood_clots BOOLEAN,
    has_infectious_disease BOOLEAN,
    has_bp_issues BOOLEAN,
    has_severe_pain BOOLEAN,
    newsletter_subscribed BOOLEAN DEFAULT FALSE,
    accepted_terms BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT customer_id_source_chk CHECK (latepoint_id IS NOT NULL OR square_id IS NOT NULL)
);

-- Create indexes for faster searching
CREATE INDEX idx_customers_latepoint_id ON customers (latepoint_id);
CREATE INDEX idx_customers_square_id ON customers (square_id);
CREATE INDEX idx_customers_email ON customers (email);

-- Create orders table
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    confirmation_code VARCHAR(50) NOT NULL UNIQUE,
    customer_id INT NOT NULL REFERENCES customers(id),
    source VARCHAR(20) NOT NULL CHECK (source IN ('square', 'latepoint', 'admin', 'acuity')),
    latepoint_order_id INT UNIQUE,
    square_order_id VARCHAR(50) UNIQUE,
    status VARCHAR(50) NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'cancelled', 'completed')),
    fulfillment_status VARCHAR(50) DEFAULT 'not_fulfilled' CHECK (fulfillment_status IN ('fulfilled', 'not_fulfilled', 'partially_fulfilled')),
    payment_status VARCHAR(50) NOT NULL CHECK (payment_status IN ('not_paid', 'partially_paid', 'fully_paid', 'processing')),
    subtotal DECIMAL(10,2) NOT NULL CHECK (subtotal >= 0),
    total DECIMAL(10,2) NOT NULL CHECK (total >= 0),
    notes TEXT,
    customer_comment TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT external_id_required CHECK (
        latepoint_order_id IS NOT NULL OR square_order_id IS NOT NULL
    )
);

CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_source ON orders(source);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_payment_status ON orders(payment_status);


-- Create order line table
CREATE TABLE order_line_items (
   id SERIAL PRIMARY KEY,
   order_id INT NOT NULL REFERENCES orders(id),
   item_id INT NOT NULL REFERENCES items(id),
   quantity INT NOT NULL DEFAULT 1,
   price INT NOT NULL,
   total INT NOT NULL,
   add_ons JSON,
   external_id VARCHAR(50) UNIQUE,
   created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
   updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
   CONSTRAINT check_quantity_positive CHECK (quantity > 0),
   CONSTRAINT check_price_positive CHECK (price >= 0),
   CONSTRAINT check_total_positive CHECK (total >= 0),
   CONSTRAINT check_total_calculation CHECK (total = price * quantity)
);

CREATE INDEX idx_order_line_items_order_id ON order_line_items(order_id);
CREATE INDEX idx_order_line_items_item_id ON order_line_items(item_id);

-- Trigger to ensure order has at least one line item
CREATE OR REPLACE FUNCTION check_order_has_items()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM order_line_items WHERE order_id = NEW.id) THEN
        RAISE EXCEPTION 'Order must have at least one item';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER ensure_order_has_items
AFTER INSERT ON orders
FOR EACH ROW
EXECUTE FUNCTION check_order_has_items();

-- Create items table
CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    external_id VARCHAR(255) NOT NULL UNIQUE, -- Unique identifier from LatePoint or Square
    name VARCHAR(255) NOT NULL UNIQUE,       -- Name of the item
    category VARCHAR(50) NOT NULL,           -- Category: service, gift_card, etc.
    type VARCHAR(50) NOT NULL DEFAULT 'service', -- Top-level classification
    base_price INT NOT NULL,                 -- Price in the smallest currency unit (e.g., pennies)
    duration INT,                            -- Duration in minutes (only for services)
    description TEXT,                        -- Detailed description of the item
    source VARCHAR(20) NOT NULL,             -- The origin: latepoint or square or acuity
    status VARCHAR(10) NOT NULL DEFAULT 'active', -- Status: 'active' or 'inactive'
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- Record creation timestamp
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- Last updated timestamp
    CHECK (source IN ('latepoint', 'square', 'acuity')), -- Ensure source is valid
    CHECK (type IN ('service', 'gift_card', 'package', 'product')), -- Valid values for type
    CHECK (status IN ('active', 'inactive'))  -- Ensure status is valid
);

-- Create composite index
CREATE INDEX idx_composite_items ON items (id, external_id, name, source);

-- or
CREATE INDEX idx_id ON items (id);
CREATE INDEX idx_external_id ON items (external_id);
CREATE INDEX idx_name ON items (name);
CREATE INDEX idx_source ON items (source);
CREATE INDEX idx_status ON items (status);

-- Create appointments table
CREATE TABLE appointments (
    id SERIAL PRIMARY KEY,
    order_line_item_id INT NOT NULL UNIQUE,
    customer_id INT NOT NULL,
    booking_code VARCHAR(50) NOT NULL,
    start_datetime TIMESTAMP NOT NULL,
    end_datetime TIMESTAMP NOT NULL,
    duration INT NOT NULL,
    agent_id INT NOT NULL,
    location_id INT NOT NULL,
    status VARCHAR(50) NOT NULL CHECK (status IN ('approved', 'pending_approval', 'cancelled', 'no_show', 'completed')), 
    payment_status VARCHAR(50) NOT NULL CHECK (payment_status IN ('not_paid', 'partially_paid', 'fully_paid', 'processing')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (order_line_item_id) REFERENCES order_line_items(id),
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (agent_id) REFERENCES agents(id),
    FOREIGN KEY (location_id) REFERENCES locations(id),
    CONSTRAINT positive_duration CHECK (duration > 0),
    CONSTRAINT end_after_start CHECK (end_datetime > start_datetime),
    CONSTRAINT start_date_not_past CHECK (start_datetime >= CURRENT_TIMESTAMP),
    CONSTRAINT end_date_not_past CHECK (end_datetime >= CURRENT_TIMESTAMP)
);

CREATE INDEX idx_appointments_customer_id ON appointments (customer_id);
CREATE INDEX idx_appointments_agent_id ON appointments (agent_id);
CREATE INDEX idx_appointments_location_id ON appointments (location_id);

-- Create transactions table  
CREATE TABLE transactions (
    id VARCHAR(50) PRIMARY KEY,
    order_id INT NOT NULL,
    amount INT NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    card_brand VARCHAR(50),
    last_4 VARCHAR(4),
    exp_month INT,
    exp_year INT,
    receipt_url VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,  
    FOREIGN KEY (order_id) REFERENCES orders(id)
);

CREATE INDEX idx_transactions_order_id ON transactions (order_id);

-- Create agents table
CREATE TABLE agents (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,  
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE INDEX idx_agents_email ON agents (email);

-- Create locations table
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    phone VARCHAR(20),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);