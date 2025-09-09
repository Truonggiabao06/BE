# 💎 Jewelry Auction System API

A complete Flask-based REST API for jewelry auction management built with Clean Architecture principles.

## 🚀 Quick Start

```bash
cd src
python app.py
```

**API Available at:** http://127.0.0.1:5000
**Swagger Documentation:** http://127.0.0.1:5000/api/docs

## 🔐 Test Credentials

- **Admin:** admin@example.com / Admin@123
- **Member:** member@example.com / Member@123
- **Staff:** staff@example.com / Staff@123
- **Manager:** manager@example.com / Manager@123

## 📁 Project Structure

```
src/
├── api/                    # API layer
│   ├── controllers/        # Request handlers (auth, jewelry, auction, bid, upload)
│   ├── middleware/         # Authentication middleware
│   └── schemas/           # Request/response validation schemas
├── domain/                # Business logic layer
│   ├── entities/          # Business entities (auction_session, jewelry_item, etc.)
│   ├── enums.py          # Enumerations (UserRole, SessionStatus, etc.)
│   ├── exceptions.py     # Custom business exceptions
│   └── repositories/     # Repository interfaces
├── infrastructure/        # Infrastructure layer
│   ├── databases/        # Database connections (MSSQL)
│   ├── models/           # SQLAlchemy models (27 tables)
│   ├── repositories/     # Data access implementations
│   └── services/         # Infrastructure services
├── services/             # Application services (auth, jewelry, auction, bidding)
├── migrations/           # Alembic database migrations
├── scripts/             # Utility scripts (seeds, test_api, etc.)
├── postman/             # Postman collection & environment
├── uploads/             # File upload storage
├── config.py            # Configuration settings
└── app.py              # Main application entry point
```

## ✅ Features

- **Authentication & Authorization** - JWT-based with role-based access control
- **Jewelry Management** - CRUD operations for jewelry items
- **Sell Request System** - Submit and manage jewelry sell requests
- **Auction Management** - Create and manage auction sessions
- **Bidding System** - Real-time bidding with validation
- **File Upload** - Image and document upload with validation
- **Payment Processing** - Payment and settlement management
- **API Documentation** - Complete Swagger/OpenAPI documentation

## 🧪 Testing

Run comprehensive API tests:
```bash
python scripts/test_api.py
```

**Latest Test Results:** 9/9 tests passed ✅

## 📚 Documentation

- **API Documentation:** `API_DOCUMENTATION.md`
- **Postman Collection:** `postman/Jewelry_Auction_API.postman_collection.json`
- **Environment:** `postman/Jewelry_Auction_Environment.postman_environment.json`