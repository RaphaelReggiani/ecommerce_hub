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
│   ├── exceptions/
│   │   ├── handlers.py
│   └── settings.py
│
├── ech/
│   ├── users/
│   │   ├── api/
│   │   │   ├── tests/
│   │   │   ├── serializers.py
│   │   │   ├── permissions.py
│   │   │   ├── throttles.py
│   │   │   ├── urls.py
│   │   │   └── views.py
│   │   │
│   │   ├── constants/
│   │   ├── services/
│   │   ├── tests/
│   │   ├── views/
│   │   ├── models.py
│   │   ├── apps.py
│   │   ├── decorators.py
│   │   ├── selectors.py
│   │   ├── exceptions.py
│   │   └── forms.py
│   │
│   └── migrations/
│
└── manage.py
```

---

# Implemented Features (Users Module)

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

---

# API Endpoints (Users)

| Endpoint                                | Description                         |
| --------------------------------------- | ----------------------------------- |
| `/api/v1/users/register/`               | User registration                   |
| `/api/v1/users/login/`                  | JWT authentication                  |
| `/api/v1/users/token/refresh/`          | Refresh access token                |
| `/api/v1/users/logout/`                 | Logout and invalidate refresh token |
| `/api/v1/users/confirm-email/`          | Email confirmation                  |
| `/api/v1/users/password-reset/`         | Request password reset              |
| `/api/v1/users/password-reset-confirm/` | Confirm password reset              |

---

# Automated Tests

The project includes automated tests using **pytest** and **Django REST Framework testing tools**.

Current tests cover:

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

Example test execution:

```
pytest ech/users/tests/
pytest ech/users/api/tests/
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
* Products module (Actual step)
* Orders system
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
