Table customers {
    id                serial       [primary key, note: "Unique identifier for each customer."]
    booking_system_id int          [unique, note: "LatePoint ID or equivalent; nullable if payment_system_id is provided."]
    payment_system_id text         [unique, note: "Square ID or equivalent; nullable if booking_system_id is provided."]
    first_name        varchar(50)  [not null, note: "Customer's first name."]
    last_name         varchar(50)  [not null, note: "Customer's last name."]
    email             varchar(100) [not null, unique, note: "Customer's email address (must be unique)."]
    phone_number      varchar(20)  [note: "Customer's phone number."]
    gender_identity   varchar(10)  [note: "Values: Male, Female, Non-Binary, Prefer Not to Say"]
    birthdate         date         [note: "Customer's date of birth."]
    primary_address   jsonb        [note: "Structured address data in JSON format."]
    session_preferences jsonb      [note: "Session preferences including aromatherapy, music, etc."]
    data_source       varchar(20)  [not null, default: 'admin', note: "Allowed values: admin, latepoint, square, acuity"]
    created_at        timestamp    [not null, default: `now()`, note: "Record creation timestamp"]
    updated_at        timestamp    [not null, default: `now()`, note: "Record last updated timestamp"]

    Indexes {
        booking_system_id [unique]
        payment_system_id [unique]
        email [unique]
    }

    Note: "Each customer must have at least one of booking_system_id or payment_system_id."
}

TableGroup CustomerSystem {
    customers
}

Table orders {
 id serial [pk]
 confirmation_code varchar(50) [unique]
 customer_id int [ref: > customers.id, not null]
 source varchar(20) [not null, note: "Allowed: 'square', 'latepoint', 'admin', 'acuity'"]
 latepoint_order_id int [unique]
 square_order_id varchar(50) [unique]
 status varchar(50) [not null, default: 'open', note: "Allowed: 'open', 'cancelled', 'completed'"]
 fulfillment_status varchar(50) [default: 'not_fulfilled', note: "Allowed: 'fulfilled', 'not_fulfilled', 'partially_fulfilled'"]
 payment_status varchar(50) [not null, note: "Allowed: 'not_paid', 'partially_paid', 'fully_paid', 'processing'"]
 subtotal decimal(10,2) [not null, note: "Must be >= 0"]
 total decimal(10,2) [not null, note: "Must be >= 0"]
 notes text
 customer_comment text
 created_at timestamp [not null, default: `CURRENT_TIMESTAMP`]
 updated_at timestamp [not null, default: `CURRENT_TIMESTAMP`]

 indexes {
   customer_id
   source
   status
   payment_status
 }

 note: 'Either latepoint_order_id or square_order_id must not be null'
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