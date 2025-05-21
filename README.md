# Expense Tracker API

![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Django](https://img.shields.io/badge/django-4.2-brightgreen)
![DRF](https://img.shields.io/badge/drf-3.14-lightgrey)
![PostgreSQL](https://img.shields.io/badge/postgres-15-blue)
![JWT](https://img.shields.io/badge/JWT-auth-orange)

A production-ready expense tracking API with JWT authentication, advanced filtering, and financial reporting capabilities. Designed for scalability and security, following RESTful principles and FAANG-level engineering standards.

## Features

### Core Functionality
- **JWT Authentication**: Secure token-based auth system with refresh tokens
- **Role-Based Access Control**: Admin/User roles with granular permissions
- **Expense Management**:
  - CRUD operations with monetary validations
  - Category-based spending tracking
  - Date-range filtering (max 5-year history)
- **Advanced Reporting**:
  - Spending distribution visualization (Matplotlib)
  - Financial summary statistics
- **Enterprise-Grade Filtering**:
  - Date ranges
  - Amount thresholds
  - Category filters
  - Multi-field sorting

### Security
- PCI-compliant input validation
- Password strength enforcement
- Rate limiting foundations
- UUID primary keys
- Hidden user field enforcement
- JWT token expiration policies

### Infrastructure
- Docker-ready architecture
- PostgreSQL optimization
- Redis caching foundations
- Automated testing framework
- CI/CD-ready structure
- API documentation (OpenAPI/Swagger)

## Tech Stack

**Backend**
- Python 3.11
- Django 4.2
- Django REST Framework 3.14
- PostgreSQL 15
- Redis 7
- Docker 24+
- JWT Authentication

**Key Libraries**
- django-filter (Advanced querying)
- matplotlib (Data visualization)
- python-decouple (Env management)
- drf-yasg (API docs)

## Installation

### Prerequisites
- Python 3.11+
- PostgreSQL 15
- Redis 7
- Docker (optional)

```bash
# Clone repository
git clone https://github.com/Korede01/expense-tracker.git
cd expense-tracker

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Database Setup
python manage.py migrate
python manage.py createsuperuser