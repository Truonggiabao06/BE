# New Jewelry Auction System Endpoints

This document describes the new endpoints added to complete the basic backend flow of the Jewelry Auction System.

## 🔐 Authentication

### POST /api/v1/auth/register
Create a new MEMBER user account.

**Request:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "role": "MEMBER"
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "user": {...},
    "access_token": "jwt_token_here",
    "refresh_token": "refresh_token_here"
  }
}
```

## 💎 Jewelry Management

### POST /api/v1/jewelry
Create a new jewelry item (STAFF/MANAGER/ADMIN only).

**Request:**
```json
{
  "title": "Diamond Ring",
  "description": "Beautiful 2-carat diamond ring",
  "photos": ["photo1.jpg", "photo2.jpg"],
  "attributes": {"material": "gold", "weight": "5.2g"},
  "weight": 5.2,
  "estimated_price": 1500.00,
  "reserve_price": 1200.00
}
```

### PATCH /api/v1/jewelry/{id}
Update jewelry item information (STAFF/MANAGER/ADMIN only).

## 📝 Sell Requests

### POST /api/v1/sell-requests
Create a sell request (MEMBER only).

**Request:**
```json
{
  "title": "Diamond Ring",
  "description": "Beautiful 2-carat diamond ring",
  "photos": ["photo1.jpg", "photo2.jpg"],
  "attributes": {"material": "gold", "weight": "5.2g"},
  "weight": 5.2,
  "seller_notes": "Inherited from grandmother"
}
```

### GET /api/v1/sell-requests
List and filter sell requests (STAFF+ only).

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 100)
- `status`: Filter by status (SUBMITTED, PRELIM_APPRAISED, etc.)

**Response:**
```json
{
  "success": true,
  "data": {
    "items": [...],
    "total": 50,
    "page": 1,
    "limit": 20
  }
}
```

### POST /api/v1/sell-requests/{id}/final-approve
Final approve a sell request (MANAGER only).

**Request:**
```json
{
  "manager_notes": "Approved for auction"
}
```

## 🏛️ Auction Sessions

### POST /api/v1/auctions/sessions
Create a new auction session (MANAGER only).

**Request:**
```json
{
  "name": "Weekly Jewelry Auction #1",
  "description": "Weekly auction featuring premium jewelry items",
  "start_at": "2024-01-15T10:00:00Z",
  "end_at": "2024-01-15T18:00:00Z"
}
```

### POST /api/v1/auctions/sessions/{sid}/items
Assign jewelry items to session (MANAGER only).

**Request:**
```json
{
  "jewelry_item_ids": ["item1-id", "item2-id"],
  "start_prices": {"item1-id": 100.00, "item2-id": 200.00},
  "step_prices": {"item1-id": 10.00, "item2-id": 20.00}
}
```

### POST /api/v1/auctions/sessions/{sid}/open
Open session for bidding (MANAGER only).

### POST /api/v1/auctions/sessions/{sid}/close
Close session and determine winners (MANAGER only).

## 💰 Bidding

### GET /api/v1/bids/sessions/{sid}/items/{itemId}/bids
List bids for a session item.

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 100)

### POST /api/v1/bids/sessions/{sid}/items/{itemId}/bids
Place a bid on a session item (MEMBER only, session must be OPEN).

**Request:**
```json
{
  "amount": 150.00
}
```

**Business Rules:**
- Session must be OPEN
- User must be enrolled in session
- Amount must be >= current_highest + step_price

## 🔒 Authorization Levels

- **GUEST**: Can view public endpoints
- **MEMBER**: Can create sell requests, place bids
- **STAFF**: Can create jewelry items, manage sell requests
- **MANAGER**: Can approve sell requests, manage auction sessions
- **ADMIN**: Full system access

## 📊 Response Format

All endpoints follow consistent response format:

**Success:**
```json
{
  "success": true,
  "message": "Operation successful",
  "data": {...}
}
```

**Error:**
```json
{
  "success": false,
  "error": "Error message",
  "code": "ERROR_CODE"
}
```

## 🧪 Testing

Run the test script to verify endpoints:

```bash
python test_endpoints.py
```

Make sure the Flask server is running on `http://localhost:5000` before running tests.

## 📝 Notes

1. All list endpoints support pagination with `page` and `limit` parameters
2. All endpoints return data in the format `{items, total, page, limit}`
3. JWT authentication is required for protected endpoints
4. Business rules are enforced at the service layer
5. Proper error handling with specific error codes
6. Swagger documentation is available at `/swagger`
