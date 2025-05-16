# PrintCraft: 3D Model Marketplace
*Enterprise Software Development (ESD) - Solo Assignment*  
University of Aberdeen

## Project Overview
PrintCraft is a specialized e-commerce platform developed as part of the Enterprise Software Development module at the University of Aberdeen. This marketplace is built using Django's Model-View-Template (MVT) architecture, providing a pure server-side solution without external APIs. The platform enables 3D model creators to sell their digital designs and buyers to purchase them.

## Architectural Approach
- **Pure Django MVT Architecture**
- **No External APIs**
- **Server-Side Rendering**
- **Session-Based Authentication**
- **Built-in Form Processing**

## Business Value
- Creators can monetize their 3D modeling skills
- Buyers can access a curated collection of 3D models
- Platform facilitates secure digital asset transactions
- Built-in model verification and preview system
- Community-driven marketplace growth

## Technology Stack
- **Framework**: Django 5.2 (MVT Architecture)
- **Database**: SQLite (Development) / PostgreSQL (Production)
- **Frontend**: Django Templates, Bootstrap 5
- **Authentication**: Django's built-in auth system
- **Session Management**: Django sessions
- **Form Processing**: Django Forms
- **Admin Interface**: Django Jazzmin

## MVT Architecture Implementation
```
PrintCraft/
├── Models (Data Layer)
│   ├── User Model
│   ├── Shop Model
│   ├── Product Model
│   └── Order Model
├── Views (Business Logic)
│   ├── Class-Based Views
│   ├── Function-Based Views
│   └── Form Processing
├── Templates (Presentation)
│   ├── Base Templates
│   ├── Page Templates
│   └── Template Tags
└── Forms
    ├── Model Forms
    ├── Custom Forms
    └── Widgets
```

## Key Features
- **User Management**: 
  - Django's auth system
  - Custom user model
  - Session-based authentication

- **Model Management**: 
  - Django model relationships
  - File upload handling
  - Form validation

- **Shop Management**: 
  - Class-based CRUD views
  - Permission mixins
  - Template inheritance

- **Transaction System**: 
  - Django forms processing
  - Session management
  - Database transactions

## Installation Guide

### Prerequisites
- Python 3.12 or higher
- pip (Python package manager)
- Virtual environment
- Git

### Setup Steps

1. Clone the repository:
```bash
git clone https://github.com/yourusername/printcraft.git
cd printcraft
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements/develop.txt
```

4. Configure the database:
```bash
python manage.py migrate
```

5. Create an admin user:
```bash
python manage.py createsuperuser
```

6. Generate sample data:
```bash
python manage.py generate_products 50
```

7. Start the development server:
```bash
python manage.py runserver
```

## Project Structure
```
apps/
├── common/          # Base models and utilities
├── users/          # User authentication
├── shops/          # Shop management
├── products/       # Product catalog
└── orders/         # Order processing
```

## Testing
- Django TestCase
- Form testing
- View testing
- Model testing
- Template tag testing

## Security Features
- CSRF protection
- XSS prevention
- Password hashing
- Session security
- Form validation

## Future Enhancements
1. **Short Term**
   - Enhanced template caching
   - Custom template tags
   - Improved form validation

2. **Long Term**
   - Advanced query optimization
   - Custom middleware
   - Batch processing

## Author
| Description | Details |
|------------|---------|
| Student ID | 52427848 |
| Module | Enterprise Software Development |
| Institution | University of Aberdeen |

## License
This project is developed as part of the Enterprise Software Development module assessment at the University of Aberdeen.
Copyright © 2025. All rights reserved.
