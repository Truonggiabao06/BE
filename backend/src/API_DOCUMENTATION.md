# 💎 Jewelry Auction System API Documentation

## 🚀 Quick Start

### 1. Start the Server
```bash
cd src
python app.py
```

The API will be available at: `http://127.0.0.1:5000`

### 2. API Documentation
- **Swagger UI**: http://127.0.0.1:5000/api/docs
- **Health Check**: http://127.0.0.1:5000/health

## 🔐 Authentication

### Login (Working Endpoint)
```bash
POST /api/v1/auth/auth
Content-Type: application/json

{
    "email": "admin@example.com",
    "password": "Admin@123"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Login successful",
    "data": {
        "user": {
            "id": "c4a876ef-817c-4694-80d7-1f7475168b6d",
            "name": "Admin User",
            "email": "admin@example.com",
            "role": "ADMIN"
        },
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
}
```

### Test Users
| Role | Email | Password |
|------|-------|----------|
| ADMIN | admin@example.com | Admin@123 |
| MANAGER | manager@example.com | Manager@123 |
| STAFF | staff@example.com | Staff@123 |
| MEMBER | member@example.com | Member@123 |

## 📋 Main Endpoints

### 🔑 Authentication
- `POST /api/v1/auth/auth` - Login (alternative endpoint)
- `POST /api/v1/auth/login` - Login (standard endpoint) ✅ **FIXED**
- `POST /api/v1/auth/register` - Register new user

### 💎 Jewelry Management
- `GET /api/v1/jewelry` - Get all jewelry items
- `POST /api/v1/jewelry` - Create jewelry item (requires auth)
- `GET /api/v1/jewelry/{id}` - Get jewelry by ID
- `PUT /api/v1/jewelry/{id}` - Update jewelry (requires auth)
- `DELETE /api/v1/jewelry/{id}` - Delete jewelry (requires auth)

### 🏷️ Sell Requests
- `GET /api/v1/sell-requests` - Get all sell requests (requires auth)
- `POST /api/v1/sell-requests` - Create sell request (requires auth)
- `GET /api/v1/sell-requests/{id}` - Get sell request by ID
- `PUT /api/v1/sell-requests/{id}/status` - Update status (staff/manager only)

### 🏛️ Auctions
- `GET /api/v1/auctions` - Get all auctions
- `POST /api/v1/auctions` - Create auction session (manager only)
- `GET /api/v1/auctions/{id}` - Get auction by ID
- `POST /api/v1/auctions/{id}/open` - Open auction session (staff)
- `POST /api/v1/auctions/{id}/close` - Close auction session (staff)

### 💰 Bidding
- `GET /api/v1/bids/sessions/{session_id}` - Get session bids ✅ **FIXED**
- `POST /api/v1/bids` - Place bid (requires auth)
- `GET /api/v1/bids/items/{item_id}` - Get item bids
- `GET /api/v1/bids/users/{user_id}` - Get user bids

### 📁 File Upload
- `POST /api/v1/upload/images` - Upload jewelry images (requires auth)
- `POST /api/v1/upload/documents` - Upload documents/certificates (requires auth)
- `GET /api/v1/upload/files/{filename}` - Serve uploaded files

## 🔒 Authorization Headers

For protected endpoints, include the JWT token:
```bash
Authorization: Bearer YOUR_ACCESS_TOKEN
```

## 📊 Example Requests

### Create Jewelry Item
```bash
curl -X POST http://127.0.0.1:5000/api/v1/jewelry \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "Diamond Ring",
    "description": "Beautiful 2-carat diamond ring",
    "category": "RING",
    "material": "GOLD",
    "weight": 15.5,
    "dimensions": "Size 7",
    "condition": "EXCELLENT",
    "estimated_value": 5000.00
  }'
```

### Get Sell Requests
```bash
curl -X GET http://127.0.0.1:5000/api/v1/sell-requests \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Place Bid
```bash
curl -X POST http://127.0.0.1:5000/api/v1/bids \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "session_item_id": "item-id-here",
    "amount": 1500.00
  }'
```

## 📁 Postman Collection

Import the provided Postman collection and environment:
- `postman/Jewelry_Auction_API.postman_collection.json`
- `postman/Jewelry_Auction_Environment.postman_environment.json`

The collection includes:
- ✅ Authentication with auto-token saving
- ✅ All main endpoints with examples
- ✅ Environment variables for different users
- ✅ Pre-configured test data

## 🗄️ Database

The system uses SQL Server with 27 tables including:
- Users & Authentication
- Jewelry Items & Categories
- Auction Sessions & Items
- Bidding System
- Sell Request Workflow
- Payment & Transaction Records

## 🎯 Status

✅ **Completed Features:**
- Authentication & Authorization (JWT)
- User Management (4 roles)
- Jewelry CRUD Operations
- Sell Request Workflow
- Auction Session Management
- Bidding System
- API Documentation (Swagger)
- Postman Collection

✅ **All Issues Fixed:**
- ✅ `/api/v1/auth/login` endpoint now works perfectly
- ✅ All bid repository methods implemented
- ✅ File upload endpoints working and tested
- ✅ Create jewelry endpoint validation fixed
- ✅ All 9/9 comprehensive tests passing

## 🔧 Development

### Database Setup
1. Ensure SQL Server is running on localhost:1433
2. Database `jewelry_auction_dev` will be created automatically
3. Sample data is seeded on first run

### Environment Variables
Check `src/.env` for configuration:
```env
DB_URL=mssql+pyodbc://sa:Giabao06%40@localhost:1433/jewelry_auction_dev?driver=ODBC+Driver+17+for+SQL+Server
JWT_SECRET_KEY=your-secret-key-change-in-production
DEBUG=true
```
