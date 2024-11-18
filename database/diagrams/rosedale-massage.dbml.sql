Table customers {
    id serial [primary key]
    latepoint_id int [unique, note: "NULL for Square-only customers"]
    square_id text [unique, note: "NULL for LatePoint-only customers"]
    first_name varchar(50) [not null]
    last_name varchar(50) [not null]
    email varchar(100) [unique, not null]
    phone varchar(20)
    gender varchar(10)
    dob date
    location varchar(100)
    postcode varchar(10)
    status varchar(20) [not null, note: "Allowed values: 'active', 'deleted', 'vip'"]
    type varchar(20) [not null, default: 'client', note: "Allowed values: 'client', 'employee'"]
    source varchar(20) [not null, note: "Allowed values: 'admin', 'latepoint', 'square'"]
    is_pregnant boolean
    has_cancer boolean
    has_blood_clots boolean
    has_infectious_disease boolean
    has_bp_issues boolean
    has_severe_pain boolean
    newsletter_subscribed boolean [default: false]
    accepted_terms boolean [default: true]
    created_at timestamp [not null, default: "CURRENT_TIMESTAMP", note: "Record creation timestamp"]
    updated_at timestamp [not null, default: "CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP", note: "Record last updated timestamp"]

    Note: "Each customer must have either latepoint_id or square_id, but not both."
}

Table orders {
    id serial [primary key]
    confirmation_code varchar(50) [not null, unique]
    customer_id int [ref: > customers.id, not null]
    latepoint_order_id int [note: "LatePoint order ID, optional"]
    square_order_id varchar(50) [note: "Square order ID, optional"]
    status varchar(50) [not null, note: "Allowed values: 'open', 'cancelled', 'completed'"]
    fulfillment_status varchar(50) [note: "e.g., 'fulfilled', 'not_fulfilled'"]
    payment_status varchar(50) [not null, note: "e.g., 'fully_paid', 'partially_paid'"]
    subtotal decimal(10, 2) [not null, note: "Subtotal before discounts, in cents"]
    total decimal(10, 2) [not null, note: "Total after discounts and taxes, in cents"]
    customer_comment text [note: "Optional comments from the customer"]
    created_at timestamp [not null, default: "CURRENT_TIMESTAMP", note: "Record creation timestamp"]
    updated_at timestamp [not null, default: "CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP", note: "Record last updated timestamp"]
    note: "Constraint: At least one of latepoint_order_id or square_order_id must not be NULL"
}

Table order_line_items {
    id serial [primary key]
    order_id int [ref: > orders.id, not null]
    item_id int [ref: > items.id, not null]
    quantity int [not null, default: 1, note: "Quantity of the item purchased"]
    price int [not null, note: "Price of the item for this order in cents"]
    total int [not null, note: "Total price for this line item (price * quantity), in cents"]
    add_ons json [note: "Optional JSON field for storing additional details like booking add-ons or service extras"]
    created_at timestamp [not null, default: "CURRENT_TIMESTAMP", note: "Record creation timestamp"]
    updated_at timestamp [not null, default: "CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP", note: "Record last updated timestamp"]
}

Table items {
    id serial [primary key, note: "Unique identifier for each item"]
    external_id varchar(255) [not null, unique, note: "Identifier from LatePoint, Square or Acuity"]
    name varchar(255) [not null, unique, note: "Name of the item, e.g., 'Swedish Massage', 'Gift Card'"]
    type varchar(50) [not null, note: "Top-level classification, e.g., 'service', 'gift_card', 'package', 'product'"]
    category varchar(50) [not null, note: "Detailed category, e.g., 'swedish blossom', 'deep tissue'"]
    base_price int [not null, note: "Base price of the item in cents"]
    duration int [note: "Duration in minutes, for services"]
    description text [note: "Detailed description of the item"]
    source varchar(20) [not null, note: "The origin system: 'latepoint' or 'square'"]
    status varchar(10) [not null, default: 'active', note: "Status of the item: 'active' or 'inactive'"]
    created_at timestamp [not null, default: "CURRENT_TIMESTAMP", note: "Record creation timestamp"]
    updated_at timestamp [not null, default: "CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP", note: "Record last updated timestamp"]

    Indexes {
        (external_id) [unique]
        (name) [unique]
        (source)
        (status)
    }
}

Table appointments {
    id serial [primary key]
    order_line_item_id int [ref: > order_line_items.id, not null, unique, note: "Links appointment to a specific order line item"]
    customer_id int [ref: > customers.id, not null]
    booking_code varchar(50) [not null]
    start_datetime timestamp [not null]
    end_datetime timestamp [not null]
    duration int [not null, note: "Duration in minutes"]
    agent_id int [ref: > agents.id, not null]
    location_id int [ref: > locations.id, not null]
    status varchar(50) [not null, note: "Allowed values: 'approved', 'pending_approval', 'cancelled', 'no_show', 'completed'"]
    payment_status varchar(50) [not null, note: "Allowed values: 'not_paid', 'partially_paid', 'fully_paid', 'processing'"]
    created_at timestamp [not null, default: "CURRENT_TIMESTAMP", note: "Record creation timestamp"]
    updated_at timestamp [not null, default: "CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP", note: "Record last updated timestamp"]

    Note: "Duration must be > 0 and end_datetime must be after start_datetime."
}

Table transactions {
    id varchar(50) [primary key, note: "Square Transaction ID, linked to orders.transaction_id"]
    order_id int [ref: > orders.id, not null]
    amount int [not null, note: "Transaction amount in cents"]
    payment_method varchar(50) [not null, note: "e.g., Credit Card, Debit Card"]
    status varchar(50) [not null, note: "e.g., COMPLETED, FAILED"]
    card_brand varchar(50) [note: "Card type used for payment, e.g., Visa"]
    last_4 varchar(4) [note: "Last 4 digits of the card used"]
    exp_month int [note: "Card expiration month"]
    exp_year int [note: "Card expiration year"]
    receipt_url varchar(255) [note: "URL to the Square payment receipt"]
    created_at timestamp [not null, default: "CURRENT_TIMESTAMP", note: "Record creation timestamp"]
    updated_at timestamp [not null, default: "CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP", note: "Record last updated timestamp"]

    Note: "The ID field now directly represents the Square Transaction ID."
}

Table agents {
    id serial [primary key]
    first_name varchar(50) [not null]
    last_name varchar(50) [not null]
    full_name varchar(100) [not null]
    email varchar(100) [not null]
    phone varchar(20)
    created_at timestamp [not null, default: "CURRENT_TIMESTAMP", note: "Record creation timestamp"]
    updated_at timestamp [not null, default: "CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP", note: "Record last updated timestamp"]
}

Table locations {
    id serial [primary key]
    name varchar(100) [not null]
    address varchar(255) [not null]
    email varchar(100)
    phone varchar(20)
    created_at timestamp [not null, default: "CURRENT_TIMESTAMP", note: "Record creation timestamp"]
    updated_at timestamp [not null, default: "CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP", note: "Record last updated timestamp"]
}