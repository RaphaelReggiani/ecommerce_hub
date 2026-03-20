# ECH (E-commerce Hub) 
### Project Language: EN-US

---

![Python](https://img.shields.io/badge/Python-3.13-blue?style=flat)
![Django](https://img.shields.io/badge/Django-6.0-green?style=flat)
![DRF](https://img.shields.io/badge/DRF-3.16-red?style=flat)

> **Note:** The name used is fictional and intended only for demonstration purposes.

**Project currently under active development**

ECH (E-commerce Hub) is a backend-focused fullstack e-commerce system built using **Python, Django, and Django REST Framework**, designed with an **API-First architecture**.

The project focuses on demonstrating **backend engineering best practices**, including authentication, modular architecture, service-layer business logic, REST API design, and automated testing.

---

# Tech Stack

* Python 3.13
* Django 6.0
* Django REST Framework (DRF) 3.16
* Django-filter
* MySQL
* HTML5 + CSS3
* JWT Authentication (SimpleJWT)
* Pytest for automated testing

---

# Key Backend Concepts Demonstrated

This project demonstrates several backend engineering concepts used in production systems:

* API-first architecture
* Service-layer business logic
* Domain-driven design principles
* Transactional consistency using `transaction.atomic`
* Concurrency protection using `select_for_update`
* Idempotent operations for order creation
* Inventory consistency in concurrent environments
* Audit event logging for operational monitoring
* Modular Django architecture
* Automated testing with pytest

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

# Architecture Diagram

```

Client
   |
   v
Django REST API
   |
   v
Service Layer
   |
   +------------------+
   |                  |
Selectors         Domain Logic
   |                  |
   +---------> Django ORM
                     |
                     v
                  Database


```
---

# Project Structure

Example structure of the backend:

```
ecommerce_hub/
│
├── core/
│   ├── exceptions/
│   │   └── handlers.py
│   ├── settings.py
│   └── urls.py
│
├── ech/
│   ├── admin.py
│   ├── apps.py
│   ├── urls.py
│
│   │
│   ├── users/
│   │   ├── api/
│   │   │   ├── tests/
│   │   │   │   ├── test_login_api.py
│   │   │   │   ├── test_logout_invalid_refresh_token_api.py
│   │   │   │   ├── test_confirm_email_api.py
│   │   │   │   ├── test_email_protections_api.py
│   │   │   │   ├── test_password_reset_confirm_api.py
│   │   │   │   ├── test_password_reset_confirm_invalid_token_api.py
│   │   │   │   ├── test_password_reset_request_api.py
│   │   │   │   ├── test_register_api.py
│   │   │   │   └── test_token_refresh_api.py
│   │   │   │
│   │   │   ├── serializers.py
│   │   │   ├── permissions.py
│   │   │   ├── throttles.py
│   │   │   ├── urls.py
│   │   │   └── views.py
│   │   │
│   │   ├── constants/
│   │   │   ├── constants.py
│   │   │   └── messages.py
│   │   │
│   │   ├── logs/
│   │   │   ├── logger.py
│   │   │   └── security_events.py
│   │   │
│   │   ├── services/
│   │   │   ├── registration_service.py
│   │   │   └── password_reset_service.py
│   │   │
│   │   ├── utils/
│   │   │   └── request_metadata.py
│   │   │
│   │   ├── tests/
│   │   │   ├── test_models.py
│   │   │   ├── test_exceptions.py
│   │   │   ├── test_selectors.py
│   │   │   ├── test_registration_service.py
│   │   │   ├── test_password_reset_service.py
│   │   │   └── test_security_events.py
│   │   │
│   │   ├── decorators.py
│   │   ├── models.py
│   │   ├── selectors.py
│   │   ├── exceptions.py
│   │   └── apps.py
│
│   ├── products/
│   │   ├── api/
│   │   │   ├── tests/
│   │   │   │   ├── test_product_create_api.py
│   │   │   │   ├── test_product_update_api.py
│   │   │   │   ├── test_product_delete_api.py
│   │   │   │   ├── test_product_list_api.py
│   │   │   │   ├── test_product_detail_api.py
│   │   │   │   └── test_product_images_api.py
│   │   │   │
│   │   │   ├── serializers.py
│   │   │   ├── permissions.py
│   │   │   ├── pagination.py
│   │   │   ├── urls.py
│   │   │   └── views.py
│   │   │
│   │   ├── services/
│   │   │   ├── product_creation_service.py
│   │   │   ├── product_delete_service.py
│   │   │   ├── product_event_service.py
│   │   │   ├── product_image_service.py
│   │   │   ├── product_inventory_service.py
│   │   │   ├── product_update_service.py
│   │   │   └── stock_service.py
│   │   │
│   │   ├── selectors/
│   │   │
│   │   ├── utils/
│   │   │   └── cache.py
│   │   │
│   │   ├── constants/
│   │   │   ├── cache.py
│   │   │   ├── constants.py
│   │   │   ├── inventory.py
│   │   │   ├── messages.py
│   │   │   ├── roles_management.py
│   │   │   ├── rules.py
│   │   │   └── storage.py
│   │   │
│   │   ├── tests/
│   │   │   ├── test_models.py
│   │   │   ├── test_selectors.py
│   │   │   ├── test_exceptions.py
│   │   │   ├── test_filters.py
│   │   │   ├── test_product_creation_service.py
│   │   │   ├── test_product_image_service.py
│   │   │   ├── test_product_update_service.py
│   │   │   ├── test_product_delete_service.py
│   │   │   └── test_product_inventory_service.py
│   │   │
│   │   ├── filters.py
│   │   ├── models.py
│   │   ├── exceptions.py
│   │   └── apps.py
│
│   ├── orders/
│   │   ├── api/
│   │   │   ├── tests/
│   │   │   │   ├── test_order_cache_api.py
│   │   │   │   ├── test_order_create_api.py
│   │   │   │   ├── test_order_list_api.py
│   │   │   │   ├── test_order_detail_api.py
│   │   │   │   ├── test_order_cancel_api.py
│   │   │   │   ├── test_order_management_list_api.py
│   │   │   │   ├── test_order_management_detail_api.py
│   │   │   │   ├── test_order_confirm_api.py
│   │   │   │   ├── test_order_processing_api.py
│   │   │   │   ├── test_order_shipping_api.py
│   │   │   │   └── test_order_delivery_api.py
│   │   │   │
│   │   │   ├── serializers.py
│   │   │   ├── permissions.py
│   │   │   ├── pagination.py
│   │   │   ├── urls.py
│   │   │   └── views.py
│   │   │
│   │   ├── services/
│   │   │   ├── cache_service.py
│   │   │   ├── order_create_service.py
│   │   │   ├── order_status_service.py
│   │   │   ├── order_cancel_service.py
│   │   │   └── order_totals_service.py
│   │   │ 
│   │   ├── utils/
│   │   │   └── cache_keys.py
│   │   │
│   │   ├── domain_events/
│   │   │   ├── dispatcher.py
│   │   │   ├── events.py
│   │   │   ├── handlers.py
│   │   │   └── registry.py
│   │   │
│   │   ├── selectors/
│   │   │
│   │   ├── constants/
│   │   │   ├── cache.py
│   │   │   ├── constants.py
│   │   │   ├── messages.py
│   │   │   └── roles_management.py
│   │   │
│   │   ├── tests/
│   │   │   ├── test_models.py
│   │   │   ├── test_exceptions.py
│   │   │   ├── test_selectors.py
│   │   │   ├── test_create_order_service.py
│   │   │   ├── test_order_status_service.py
│   │   │   ├── test_cancel_order_service.py
│   │   │   ├── test_order_totals_service.py
│   │   │   ├── test_domain_events.py
│   │   │   ├── test_cache_selectors.py
│   │   │   ├── test_cache_invalidation.py
│   │   │   └── test_filters.py
│   │   │
│   │   ├── filters.py
│   │   ├── models.py
│   │   ├── exceptions.py
│   │   └── apps.py
│
│   ├── payments/
│   │   ├── api/
│   │   │   ├── tests/
│   │   │   │   ├── test_payment_create_api.py
│   │   │   │   ├── test_payment_list_api.py
│   │   │   │   ├── test_payment_detail_api.py
│   │   │   │   ├── test_payment_process_api.py
│   │   │   │   ├── test_payment_cancel_api.py
│   │   │   │   ├── test_payment_refund_api.py
│   │   │   │   ├── test_payment_transaction_list_api.py
│   │   │   │   └── test_payment_management_detail_api.py
│   │   │   │
│   │   │   ├── serializers.py
│   │   │   ├── permissions.py
│   │   │   ├── pagination.py
│   │   │   ├── urls.py
│   │   │   └── views.py
│   │   │
│   │   ├── services/
│   │   │   ├── cache_service.py
│   │   │   ├── payment_creation_service.py
│   │   │   ├── payment_processing_service.py
│   │   │   ├── payment_status_service.py
│   │   │   ├── payment_refund_service.py
│   │   │   └── payment_log_service.py
│   │   │ 
│   │   ├── utils/
│   │   │   └── cache_keys.py
│   │   │
│   │   ├── domain_events/
│   │   │   ├── dispatcher.py
│   │   │   ├── events.py
│   │   │   ├── handlers.py
│   │   │   └── registry.py
│   │   │
│   │   ├── selectors/
│   │   │
│   │   ├── constants/
│   │   │   ├── cache.py
│   │   │   ├── constants.py
│   │   │   ├── messages.py
│   │   │   └── roles_management.py
│   │   │
│   │   ├── tests/
│   │   │   ├── test_models.py
│   │   │   ├── test_exceptions.py
│   │   │   ├── test_selectors.py
│   │   │   ├── test_payment_create_service.py
│   │   │   ├── test_payment_status_service.py
│   │   │   ├── test_payment_processing_service.py
│   │   │   ├── test_payment_refund_service.py
│   │   │   ├── test_domain_events.py
│   │   │   ├── test_cache_selectors.py
│   │   │   ├── test_cache_invalidation.py
│   │   │   └── test_filters.py
│   │   │
│   │   ├── filters.py
│   │   ├── models.py
│   │   ├── exceptions.py
│   │   ├── selectors.py
│   │   └── apps.py
│ 
├── ech_web/
│   └── ...
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
* **OrderEvent** – operational event logging with event-driven architecture
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

| Method | Endpoint | Description |
|------|------|------|
| POST | `/api/v1/users/register/` | User registration |
| POST | `/api/v1/users/login/` | JWT authentication |
| POST | `/api/v1/users/token/refresh/` | Refresh access token |
| POST | `/api/v1/users/logout/` | Logout and invalidate refresh token |
| POST | `/api/v1/users/confirm-email/` | Email confirmation |
| POST | `/api/v1/users/password-reset/` | Request password reset |
| POST | `/api/v1/users/password-reset-confirm/` | Confirm password reset |

---

## Products

| Method | Endpoint | Description |
|------|------|------|
| POST | `/api/v1/products/` | Create product |
| GET | `/api/v1/products/list/` | List products (paginated) |
| GET | `/api/v1/products/{product_id}/` | Retrieve product details |
| POST | `/api/v1/products/{product_id}/images/` | Upload product images |
| PATCH | `/api/v1/products/{product_id}/` | Update product |
| DELETE | `/api/v1/products/{product_id}/` | Soft delete product |

---

## Orders (Customer)

| Method | Endpoint | Description |
|------|------|------|
| GET | `/api/v1/orders/` | List authenticated customer orders |
| POST | `/api/v1/orders/create/` | Create new order |
| GET | `/api/v1/orders/{order_id}/` | Retrieve order details |
| POST | `/api/v1/orders/{order_id}/cancel/` | Cancel order |

---

## Orders (Management)

| Method | Endpoint | Description |
|------|------|------|
| GET | `/api/v1/orders/management/` | List all orders (staff) |
| GET | `/api/v1/orders/management/{order_id}/` | Retrieve order details (staff) |
| POST | `/api/v1/orders/management/{order_id}/confirm/` | Confirm order |
| POST | `/api/v1/orders/management/{order_id}/start-processing/` | Start order processing |
| POST | `/api/v1/orders/management/{order_id}/ship/` | Ship order |
| POST | `/api/v1/orders/management/{order_id}/deliver/` | Mark order as delivered |
| POST | `/api/v1/orders/management/{order_id}/cancel/` | Cancel order (staff) |

---

# Automated Tests

The project includes an extensive automated test suite covering domain logic and API endpoints, using **pytest** and **Django REST Framework testing tools**.

---

# Testing Strategy

The project follows a domain-first testing strategy.

1. Domain layer tests validate business rules and services
2. Selector tests validate database queries
3. API tests validate endpoint behavior and permissions

This ensures business logic remains stable independently from the API layer.

---

## Users

### Tests Coverage Status:

* Domain: 99 tests
* API: 29 tests

### Users Domain Tests

### Domain Models

* custom user creation and manager behavior
* email normalization and uniqueness validation
* role-based behavior and permissions flags (`is_staff`, `is_superuser`)
* corporate email enforcement for staff roles
* age validation boundaries (min/max)
* default field values (`is_active`, `email_confirmed`)
* model properties (`is_superadmin`, `can_create_staff`)
* string representation consistency

### User Token Model

* token creation and uniqueness
* expiration validation
* expired token rejection
* token usage tracking (`used` flag)
* token lifecycle methods (`is_expired`, `mark_as_used`)
* metadata field behavior

### Domain Exceptions

* base domain exception behavior
* default vs custom message handling
* exception hierarchy validation
* authentication and token-related exceptions
* role and access-related exceptions

### Query Selectors

Tests validate database query behavior and filtering logic:

* retrieving user by ID
* retrieving user by email (case-insensitive)
* listing users by role
* listing active users
* listing staff users
* retrieving email confirmation tokens
* retrieving valid tokens (non-expired, unused, correct type)
* handling of invalid or missing records

### Registration Service

* user registration workflow
* default role assignment
* duplicate email protection (domain-level validation)
* inactive and unconfirmed user initialization
* email confirmation token generation
* replacement of existing confirmation tokens
* transaction-safe email scheduling (`on_commit`)
* email confirmation flow
* activation and confirmation state updates
* invalid and expired token handling

### Password Reset Service

* password reset request workflow
* protection against user enumeration
* handling inactive or non-existent users
* reset token creation and replacement
* transaction-safe email scheduling
* password reset execution
* password update and hashing validation
* token invalidation and usage tracking
* invalid and expired token handling

### Security Logging

Tests validate security event logging behavior:

* login success and failure events
* user registration logging
* email confirmation logging
* password change logging
* invalid token logging
* password reset request logging
* structured logging payload validation
* request metadata integration (IP, user agent, request ID)

---

### Users API Tests

### Authentication & Access Control

* login with valid credentials
* authentication failure (invalid credentials)
* inactive account protection
* email confirmation requirement enforcement

### Registration API

* successful user registration
* validation of required fields
* duplicate email protection
* response structure validation

### Token Management

* JWT token refresh flow
* invalid and malformed token handling
* logout with invalid refresh token

### Email Confirmation API

* successful email confirmation
* invalid token handling
* expired token handling

### Password Reset APIs

#### Request Password Reset

* valid email request handling
* non-existent email protection (no information leakage)
* inactive user handling

#### Confirm Password Reset

* successful password reset
* invalid token handling
* expired token handling
* payload validation

### Email Protection Tests

* access restrictions for unconfirmed users
* validation of protected endpoints
* enforcement of authentication and confirmation rules

---

## Products

### Tests Coverage Status:

* Domain: 114 tests
* API: 24 tests

### Products Domain Tests

### Domain Models

* product creation and core field validation
* UUID primary key generation
* product type choices validation
* price and discount field behavior
* active/inactive state handling
* discount logic validation (`has_discount`)
* main image resolution logic
* inventory shortcut property behavior
* model ordering by `created_at`
* string representations

### Product Inventory Model

* one-to-one relationship with product
* default inventory value
* inventory updates and persistence
* uniqueness constraint enforcement
* string representation validation

### Product Image Model

* image creation and relationship with product
* file upload path validation
* file extension validation (jpg, jpeg, png, webp)
* display order validation (`order >= 1`)
* unique constraint per product (`product + order`)
* ordering behavior by display order
* string representation validation

### Product Event Log Model

* event creation and lifecycle tracking
* UUID primary key generation
* event type validation
* optional performer handling
* metadata storage behavior
* ordering by `created_at`
* string representation validation

### Domain Exceptions

* validation error inheritance consistency
* permission error inheritance consistency
* default message validation
* formatted message validation (min/max images)
* exception hierarchy consistency

### Query Selectors

Tests validate query behavior and filtering logic:

* retrieving product by ID
* retrieving active product by ID
* listing all active products
* filtering products by type
* retrieving products with discount
* search by name and brand (case-insensitive)
* retrieving products created by user
* retrieving available products (inventory > 0)
* handling of non-existent records

### Product Creation Service

* product creation workflow
* permission validation for allowed roles
* product type validation
* price validation (null, zero, negative)
* discount validation (negative, >= price)
* inventory validation (negative values)
* creation of inventory record
* handling of optional discount
* transactional rollback on failure

### Product Update Service

* updating single field
* updating multiple fields
* updating text fields
* persistence of updated data
* return of updated product instance
* handling non-existent product
* no-op update (no fields provided)

### Product Delete Service

* soft delete behavior (`is_active=False`)
* persistence of state change
* record retention in database
* ensuring only active flag is modified
* handling non-existent product

### Product Image Service

* adding single image
* adding multiple images
* empty upload handling
* maximum image limit enforcement
* sequential order assignment
* continuation of order after existing images
* bulk creation behavior
* handling non-existent product

### Product Image Validation

* minimum image requirement enforcement
* validation failure below minimum threshold
* validation success at minimum threshold
* validation success above minimum threshold
* validation failure when no images exist

### Product Inventory Service

* decreasing inventory successfully
* exact inventory depletion (to zero)
* insufficient inventory protection
* persistence of inventory updates
* return of updated inventory instance
* handling missing inventory record

### Product Filters

Tests validate filtering behavior for product listing:

* filtering by minimum price (`price_min`)
* filtering by maximum price (`price_max`)
* filtering by price range
* filtering by brand (case-insensitive)
* filtering by product type
* combined filter queries
* empty result handling

---

### Products API Tests

### Product Creation API

* successful product creation
* validation of required fields
* permission enforcement
* invalid payload handling

### Product Listing API

* listing active products
* pagination behavior
* filtering integration
* response structure validation

### Product Detail API

* retrieving product by ID
* nested related data (images, inventory)
* handling non-existent products
* response structure validation

### Product Update API

* successful product update
* validation of invalid fields
* permission enforcement
* partial update behavior

### Product Deletion API

* soft delete via API
* permission enforcement
* validation of non-existent product
* response structure validation

### Product Image API

* image upload workflow
* multiple image upload handling
* maximum image limit enforcement
* response validation

---

## Orders

### Tests Coverage Status:

* Domain: 230 tests
* API: 87 tests

### Orders Domain Tests

### Domain Models

* order creation and relationships
* order item associations
* order totals one-to-one integrity
* order lifecycle timestamps
* order events audit trail
* order notes relationships
* model ordering behavior
* string representations

### Domain Exceptions

* order not found validation
* permission protection
* duplicate order protection
* invalid status transition handling
* cancellation rule validation
* inventory validation
* invalid payment and shipping state protections

### Query Selectors

Tests validate query optimizations and retrieval logic:

* retrieving orders by ID
* retrieving orders with related entities
* listing orders by customer
* listing orders by status
* listing orders by payment status
* listing orders by shipping status
* listing recent orders
* management dashboard queries
* database locking for updates (`select_for_update`)

### Order Creation Service

* order creation workflow
* product availability validation
* inventory validation
* snapshot product data creation
* totals calculation
* lifecycle initialization
* address snapshot creation
* order event registration
* idempotency key protection
* transactional rollback validation

### Order Status Service

* order confirmation
* processing transition
* shipping transition
* delivery transition
* lifecycle timestamp updates
* audit event registration
* invalid status transition protection

### Order Cancellation Service

* order cancellation workflow
* cancellation rule validation
* prevention of cancelling shipped/delivered orders
* prevention of cancelling already cancelled orders
* lifecycle cancellation timestamp update
* inventory restoration after cancellation
* cancellation event audit log

### Order Totals Service

* totals recalculation from order items
* discount calculation
* subtotal and grand total consistency
* updating existing totals
* creating totals when missing
* recalculation after item changes
* zero totals when order has no items

### Operational Filters

Tests validate filtering behavior for operational endpoints:

* filtering by order status
* filtering by payment status
* filtering by shipping status
* filtering by customer email
* filtering by customer name
* filtering by creation date range
* case-insensitive filtering behavior
* combined filter queries

### Order Events Domains

* dispatch call registered
* dispatch for cancelled events

### Order Caching

Tests validate caching behavior and consistency for order retrieval:

* caching of order detail by ID
* caching of management order detail
* cache hit returns consistent data
* caching of non-existent orders (None responses)
* stale data behavior before cache invalidation
* fresh data retrieval after cache invalidation
* cache isolation between tests (`cache.clear()` usage)

### Cache Invalidation

Tests validate that domain services correctly invalidate cache:

* cache invalidation after order creation
* cache invalidation after order cancellation
* cache invalidation after order confirmation
* cache invalidation after processing transition
* cache invalidation after shipping transition
* cache invalidation after delivery transition
* fresh data retrieval after each mutation
* validation that cached data is replaced after state changes

---

### Orders API Tests

### Authentication & Access Control

* JWT authentication enforcement
* unauthorized access protection (401)
* permission-based access control (403)
* customer vs staff access boundaries
* resource ownership validation (customers can only access their own orders)

### Order Detail API

* retrieving order details by ID
* nested related data serialization (items, totals, lifecycle, address)
* UUID serialization consistency
* access restriction for non-owners
* handling non-existent orders (404)
* response structure validation

### Customer Orders List API

* listing orders for authenticated customer
* ensuring only customer-owned orders are returned
* ordering by `created_at` (descending)
* pagination behavior
* empty state handling

### Order Management List API (Staff)

* access restricted to staff roles
* listing all orders for management dashboard
* ordering by `created_at` (descending)
* pagination validation
* filtering integration with:
  * order status
  * payment status
  * shipping status
  * customer email
  * customer name
  * date range (created_after / created_before)
* combined filters behavior

### Order Management Detail API (Staff)

* retrieving full order detail for staff
* nested entities validation (items, events, notes, lifecycle)
* timestamp fields validation (confirmed, shipped, delivered, etc.)
* handling non-existent orders
* permission enforcement

### Order Creation API

* successful order creation
* validation of empty items payload
* product availability validation
* inventory validation
* address validation
* idempotency key behavior
* transactional consistency on failure
* response payload validation

### Order Status APIs

#### Confirm Order

* successful confirmation flow
* validation of invalid transitions
* lifecycle timestamp update (`confirmed_at`)
* response payload validation

#### Start Processing

* successful processing transition
* validation of invalid transitions
* lifecycle timestamp update (`processing_at`)
* response payload validation

#### Ship Order

* successful shipping transition
* validation of invalid transitions
* shipping status update
* lifecycle timestamp update (`shipped_at`)
* response payload validation

#### Deliver Order

* successful delivery transition
* validation of invalid transitions
* shipping status update
* lifecycle timestamp update (`delivered_at`)
* response payload validation

### Order Cancellation API

* successful cancellation flow
* validation of cancellation rules
* prevention of invalid cancellations
* inventory restoration behavior
* lifecycle timestamp update (`cancelled_at`)
* cancellation event registration
* response payload validation
* handling service-level exceptions (400 responses)

### Caching Behavior (API Layer)

* cache consistency after order mutations
* cache invalidation after:
  * order creation
  * order status transitions
  * order cancellation
* ensuring fresh data is returned after updates
* preventing stale responses in detail endpoints

### Order Caching (API Layer)

Tests validate caching behavior through API endpoints:

* fresh data returned after order cancellation via API
* fresh data returned after order confirmation via API
* fresh data returned after processing transition via API
* fresh data returned after shipping transition via API
* fresh data returned after delivery transition via API
* repeated requests return consistent data (cache stability)
* prevention of stale data in order detail endpoints

---

Example test execution:

```
pytest ech/users/tests/
pytest ech/users/api/tests/

pytest ech/products/tests/
pytest ech/products/api/tests/

pytest ech/orders/tests/
pytest ech/orders/api/tests/
```

---

# Running the Project

Clone the repository:

```
git clone https://github.com/RaphaelReggiani/ecommerce_hub
cd ech
cd ech_web
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
* Orders system ✔
* Payment integration (*Current step*)
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
