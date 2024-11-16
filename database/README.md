# Rosedale Database

## Overview

The Rosedale database is designed to manage and track all aspects of Rosedale's operations, including customer information, appointments, orders, transactions, and inventory (services and products). This schema ensures efficient storage and retrieval of data while supporting integrations with systems like LatePoint and Square.

---

## Database Schema

### Key Tables:
1. **`customers`**: Stores customer information from LatePoint and Square in a unified table.
2. **`orders`**: Manages orders placed by customers, linked to the services or products purchased.
3. **`order_line_items`**: Tracks individual items (e.g., massage services, gift cards) within an order.
4. **`items`**: Acts as a catalog for all services, products, and gift cards available.
5. **`appointments`**: Stores information about customer bookings, such as timing, location, and status.
6. **`transactions`**: Tracks financial transactions processed through Square.
7. **`agents`**: Details about employees or massage therapists.
8. **`locations`**: Information about studio locations.

---

## Table Details

### Customers
Tracks information about Rosedale's clients and their origin (LatePoint, Square, or both).
- **Key Fields**: `first_name`, `last_name`, `email`, `status` (e.g., active, deleted, VIP), `type` (client, employee).

### Orders
Represents customer orders, linked to the items purchased and transactions processed.
- **Key Fields**: `confirmation_code`, `status` (e.g., approved, pending approval), `subtotal`, `total`.

### Order Line Items
Tracks individual items within an order.
- **Key Fields**: `order_id`, `item_id`, `quantity`, `add_ons` (JSON for service extras or customizations).

### Items
Catalog of all services, products, and gift cards offered by Rosedale.
- **Key Fields**: `name`, `category` (service, gift_card, product), `base_price`, `duration`.

### Appointments
Manages booking details, including assigned therapists and location.
- **Key Fields**: `order_line_item_id`, `booking_code`, `status` (e.g., approved, completed), `payment_status`.

### Transactions
Logs payments processed via Square.
- **Key Fields**: `id` (Square transaction ID), `order_id`, `amount`, `payment_method`, `status`.

### Agents
Details about employees or therapists.
- **Key Fields**: `first_name`, `last_name`, `email`.

### Locations
Information about studio locations.
- **Key Fields**: `name`, `address`, `phone`.

---

## Key Features

- **Unified Customer Data**: Combines LatePoint and Square customer information in a single table.
- **Service Extras**: Supports optional add-ons for appointments stored in JSON format.
- **Timestamps**: All tables include `created_at` and `updated_at` fields for tracking changes.
- **Status Management**:
  - Appointments: Tracks statuses like `approved`, `pending_approval`, `cancelled`.
  - Orders: Manages fulfillment and payment statuses.

---

## Integrations

- **LatePoint**:
  - Appointments and services are linked to orders and customers through this integration.
- **Square**:
  - Transactions are fully handled by Square, ensuring seamless payment processing.

---

## Example Queries

### Fetch All Orders for a Customer
```sql
SELECT 
    o.id AS order_id, 
    o.confirmation_code, 
    o.total, 
    o.status
FROM 
    orders o
JOIN 
    customers c ON o.customer_id = c.id
WHERE 
    c.email = 'customer@example.com';
