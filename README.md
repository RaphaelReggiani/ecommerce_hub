# ECH (E-commerce Hub) EN-US

![Python](https://img.shields.io/badge/Python-3.13-blue?style=flat)
![Django](https://img.shields.io/badge/Django-4.2-green?style=flat)
![DRF](https://img.shields.io/badge/DRF-3.14-red?style=flat)

> **Note:** The name used is fictional and intended only for demonstration purposes.

**Project currently under active development**

ECH (E-commerce Hub) is a backend-focused fullstack e-commerce system built using **Python, Django, and Django REST Framework**, designed with an **API-First architecture**.

The project focuses on demonstrating **backend engineering best practices**, including authentication, modular architecture, service-layer business logic, REST API design, and automated testing.

---

# Tech Stack

* Python 3.13
* Django
* Django REST Framework (DRF)
* MySQL
* HTML5 + CSS3
* JWT Authentication (SimpleJWT)
* Pytest for automated testing

---

# Architecture Overview

The backend follows a modular and layered architecture designed to improve **maintainability, scalability, and testability**.

Core architectural layers include:

### API Layer

Handles HTTP communication using Django REST Framework.

* Views
* Serializers
* Permissions
* Throttling

### Service Layer

Responsible for implementing business logic and orchestrating operations.

Examples:

* user registration
* email confirmation
* password reset flow

### Selector Layer

Handles optimized database queries and data retrieval.

### Models Layer

Defines database schema and relationships using Django ORM.

### Constants Layer

Centralizes system messages and configuration values.

---

# Project Structure

Example structure of the backend:

```
ecommerce_hub/
│
├── core/
│ ├── exceptions/
│ │ ├── handlers.py
│ │
│ └── settings.py
│
├── ech/
│
│ ├── users/
│ │ ├── api/
│ │ │ ├── tests/
│ │ │ ├── serializers.py
│ │ │ ├── permissions.py
│ │ │ ├── throttles.py
│ │ │ ├── urls.py
│ │ │ └── views.py
│ │ │
│ │ ├── constants/
│ │ ├── services/
│ │ ├── selectors/
│ │ ├── tests/
│ │ ├── views/
│ │ ├── models.py
│ │ ├── decorators.py
│ │ ├── exceptions.py
│ │ └── forms.py
│
│ ├── products/
│ │ ├── api/
│ │ │ ├── tests/
│ │ │ ├── serializers.py
│ │ │ ├── permissions.py
│ │ │ ├── pagination.py
│ │ │ ├── urls.py
│ │ │ └── views.py
│ │ │
│ │ ├── services/
│ │ ├── selectors/
│ │ ├── infrastructure/
│ │ │ └── cache.py
│ │ │
│ │ ├── constants/
│ │ ├── tests/
│ │ ├── filters.py
│ │ ├── models.py
│ │ ├── exceptions.py
│ │ └── apps.py
│
│ ├── orders/
│ │ ├── api/
│ │ │ ├── tests/
│ │ │ ├── serializers.py
│ │ │ ├── permissions.py
│ │ │ ├── pagination.py
│ │ │ ├── urls.py
│ │ │ └── views.py
│ │ │
│ │ ├── services/
│ │ │ ├── create_order_service.py
│ │ │ ├── order_status_service.py
│ │ │ ├── cancel_order_service.py
│ │ │ └── order_totals_service.py
│ │ │
│ │ ├── selectors/
│ │ ├── constants/
│ │ ├── tests/
│ │ ├── filters.py
│ │ ├── models.py
│ │ ├── exceptions.py
│ │ └── apps.py
│
│ └── migrations/
│
└── manage.py

```

---

# Implemented Features

## Users Module

### Authentication

* JWT login authentication
* Access and refresh token mechanism
* Token refresh endpoint
* Secure logout with refresh token invalidation

### User Management

* User registration
* Email confirmation system
* Password reset via email
* Protection against inactive accounts
* Role-based permission system

### Security Features

* Token expiration validation
* Invalid token protections
* Email verification requirement
* Security-focused API responses
* Security logging

---

## Products Module

### Product Management

* Product creation with validation rules
* Product update with partial updates
* Soft deletion for products
* Product image upload with ordering
* Separate inventory model for stock management

### Inventory Control

* Dedicated inventory table (`ProductInventory`)
* Atomic stock operations
* Database-level locking to prevent overselling

### Performance Optimization

* Product detail caching
* Smart caching for product list endpoints
* Optimized database queries using `select_related` and `prefetch_related`
* Indexed fields for faster filtering and sorting

### Audit Logging

* Event logging for product actions
* Logged events include:
  * product creation
  * product updates
  * product deletion
  * product image uploads

This provides a full audit trail for product management operations.

### Filtering and Search

* Product filtering by attributes
* Full-text search on product fields
* Ordering by price, creation date and name
* Paginated product listings

---

# Orders Module

### Order Creation

* Atomic order creation using a service layer
* Support for multiple order items
* Product snapshot storage for historical accuracy
* Idempotency key support to prevent duplicate orders
* Automatic calculation of order totals

### Order Components

Orders are composed of multiple related entities:

* **Order** – main aggregate root
* **OrderItem** – purchased products snapshot
* **OrderTotals** – calculated financial totals
* **OrderAddress** – shipping address snapshot
* **OrderLifecycle** – timestamps for order lifecycle events
* **OrderEvent** – operational event logging
* **OrderNote** – communication logs between staff and customer

### Inventory Safety

* Stock validation during order creation
* Database-level row locking using `select_for_update`
* Atomic stock updates to prevent overselling
* Automatic stock restoration when orders are cancelled

### Order Lifecycle Management

Orders follow a controlled lifecycle:

```
PENDING
→ CONFIRMED
→ PROCESSING
→ SHIPPED
→ DELIVERED
```

Additional transitions:

```
CANCELLED
REFUNDED
```

Lifecycle timestamps are tracked in the `OrderLifecycle` model.

### Operational Event Logging

Every important order action creates an `OrderEvent`, including:

* order creation
* order confirmation
* processing start
* shipping
* delivery
* cancellation

This ensures a full operational audit trail.

### Concurrency Protection

To avoid race conditions in order processing:

* Row-level locking with `select_for_update`
* Transactional service layer (`transaction.atomic`)
* Safe inventory updates using database expressions (`F()`)

### Filtering and Management

Staff management endpoints support:

* filtering by order status
* filtering by payment status
* filtering by shipping status
* filtering by customer email
* paginated order listing

---

# API Endpoints

## Users

| Endpoint                                | Description                         |
|-----------------------------------------|-------------------------------------|
| `/api/v1/users/register/`               | User registration                   |
| `/api/v1/users/login/`                  | JWT authentication                  |
| `/api/v1/users/token/refresh/`          | Refresh access token                |
| `/api/v1/users/logout/`                 | Logout and invalidate refresh token |
| `/api/v1/users/confirm-email/`          | Email confirmation                  |
| `/api/v1/users/password-reset/`         | Request password reset              |
| `/api/v1/users/password-reset-confirm/` | Confirm password reset              |

---

## Products

| Endpoint                                    | Description                     |
|---------------------------------------------|---------------------------------|
| `/api/v1/products/`                         | Create product                  |
| `/api/v1/products/list/`                    | List products (paginated)       |
| `/api/v1/products/{product_id}/`            | Retrieve product details        |
| `/api/v1/products/{product_id}/images/`     | Upload product images           |
| `/api/v1/products/{product_id}/` (PATCH)    | Update product                  |
| `/api/v1/products/{product_id}/` (DELETE)   | Soft delete product             |

---

## Orders (Customer)

| Endpoint | Description |
|--------|-------------|
| `/api/v1/orders/` | List authenticated customer orders |
| `/api/v1/orders/create/` | Create new order |
| `/api/v1/orders/{order_id}/` | Retrieve order details |
| `/api/v1/orders/{order_id}/cancel/` | Cancel order |

---

## Orders (Management)

| Endpoint | Description |
|--------|-------------|
| `/api/v1/orders/management/` | List all orders (staff) |
| `/api/v1/orders/management/{order_id}/` | Retrieve order details (staff) |
| `/api/v1/orders/management/{order_id}/confirm/` | Confirm order |
| `/api/v1/orders/management/{order_id}/start-processing/` | Start order processing |
| `/api/v1/orders/management/{order_id}/ship/` | Ship order |
| `/api/v1/orders/management/{order_id}/deliver/` | Mark order as delivered |
| `/api/v1/orders/management/{order_id}/cancel/` | Cancel order (staff) |

---

# Automated Tests

The project includes automated tests using **pytest** and **Django REST Framework testing tools**.

Current tests cover:

### Users

* user creation
* invalid role validation
* expired token validation
* inactive account protection
* email confirmation flow
* register API
* login API
* token refresh API
* logout security tests
* password reset request API
* password reset confirmation API
* invalid token protections

### Products

* product creation API
* product listing API
* product detail API
* product update API
* product deletion API
* product image upload API
* permission validation
* pagination consistency
* filtering and search behavior
* edge cases for product data validation

Example test execution:

```
pytest ech/users/tests/
pytest ech/users/api/tests/
pytest ech/products/tests/
pytest ech/products/api/tests/
```

---

# Running the Project

Clone the repository:

```
git clone https://github.com/your-username/ech.git
cd ech
```

Create a virtual environment:

```
python -m venv venv
```

Activate the environment:

Windows:

```
venv\Scripts\activate
```

Linux / Mac:

```
source venv/bin/activate
```

Install dependencies:

```
pip install -r requirements.txt
```

Run migrations:

```
python manage.py migrate
```

Start the development server:

```
python manage.py runserver
```

---

# Development Roadmap

Planned modules:

* Users module ✔
* Products module ✔
* Orders system (Actual step)
* Payment integration
* Shipping system
* Reviews system
* Notifications system
* Analytics system
* Admin dashboard

---

# Purpose of the Project

This project is part of my backend development portfolio and aims to demonstrate:

* REST API design
* authentication and security practices
* scalable Django architecture
* separation of concerns
* service-layer design
* automated testing
* production-oriented backend development

---

# Author

Raphael Regiani Silva

LinkedIn:
https://www.linkedin.com/in/raphael-regiani-b1ba73a5/

GitHub:
https://github.com/RaphaelReggiani

Portfolio:
https://raphaelreggiani.github.io/portfolio/
