# 📚 Jewelry Auction System API Documentation

## 🌟 Overview

**Jewelry Auction System API** là một RESTful API hoàn chỉnh cho hệ thống đấu giá trang sức trực tuyến, được xây dựng với Flask và Clean Architecture.

### 🎯 Key Features
- **Authentication & Authorization** - JWT-based với email verification
- **Auction Management** - Tạo và quản lý phiên đấu giá
- **Real-time Bidding** - Đặt giá real-time với WebSocket
- **Payment Processing** - Xử lý thanh toán đa phương thức
- **Notification System** - Thông báo real-time và email

### 🔧 Technical Stack
- **Backend**: Flask, SQLAlchemy, SQL Server
- **Authentication**: JWT, Email Verification
- **Real-time**: WebSocket (Socket.IO)
- **Documentation**: OpenAPI/Swagger

---

## 🚀 Getting Started

### Base URL
```
Production: https://api.jewelry-auction.com
Development: http://127.0.0.1:5000
```

### Authentication
API sử dụng JWT Bearer tokens:
```http
Authorization: Bearer <your-jwt-token>
```

### Response Format
Tất cả responses đều có format chuẩn:
```json
{
  "success": true,
  "message": "Success message",
  "data": { ... },
  "pagination": { ... } // Chỉ có trong paginated responses
}
```

---

## 🔐 Authentication Endpoints

### POST /api/auth/register
Đăng ký tài khoản mới

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "first_name": "Nguyễn",
  "last_name": "Văn A",
  "phone": "0901234567"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Đăng ký thành công! Vui lòng kiểm tra email để xác thực.",
  "data": {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "full_name": "Nguyễn Văn A",
      "is_email_verified": false
    }
  }
}
```

### POST /api/auth/login
Đăng nhập

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Đăng nhập thành công!",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
      "id": 1,
      "email": "user@example.com",
      "role": "user",
      "is_email_verified": true
    }
  }
}
```

### POST /api/auth/verify-email
Xác thực email

**Request Body:**
```json
{
  "email": "user@example.com",
  "verification_code": "123456"
}
```

---

## 🏺 Auction Items Endpoints

### GET /api/auction-items
Lấy danh sách sản phẩm đấu giá

**Query Parameters:**
- `page` (int): Trang hiện tại (default: 1)
- `limit` (int): Số items per page (default: 20, max: 100)
- `category` (string): Lọc theo category
- `status` (string): Lọc theo status
- `min_price` (int): Giá tối thiểu
- `max_price` (int): Giá tối đa

**Response:**
```json
{
  "success": true,
  "message": "Lấy danh sách sản phẩm thành công",
  "data": [
    {
      "id": 1,
      "title": "Nhẫn kim cương 2 carat",
      "description": "Nhẫn kim cương thiên nhiên...",
      "category": "ring",
      "condition": "excellent",
      "starting_price": 50000000,
      "current_price": 55000000,
      "images": ["image1.jpg", "image2.jpg"],
      "status": "active",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

### POST /api/auction-items
Tạo sản phẩm đấu giá mới (Requires authentication)

**Request Body:**
```json
{
  "title": "Nhẫn kim cương 2 carat",
  "description": "Mô tả chi tiết sản phẩm...",
  "category": "ring",
  "condition": "excellent",
  "starting_price": 50000000,
  "images": ["base64_image_1", "base64_image_2"]
}
```

### GET /api/auction-items/categories
Lấy danh sách categories

**Response:**
```json
{
  "success": true,
  "message": "Lấy danh sách categories thành công",
  "data": {
    "categories": [
      {"value": "ring", "label": "Nhẫn"},
      {"value": "necklace", "label": "Dây chuyền"},
      {"value": "earrings", "label": "Bông tai"},
      {"value": "bracelet", "label": "Vòng tay"},
      {"value": "watch", "label": "Đồng hồ"},
      {"value": "brooch", "label": "Trâm cài"},
      {"value": "pendant", "label": "Mặt dây chuyền"},
      {"value": "other", "label": "Khác"}
    ]
  }
}
```

---

## 🎯 Auction Sessions Endpoints

### GET /api/auction-sessions
Lấy danh sách phiên đấu giá

**Query Parameters:**
- `page`, `limit`: Pagination
- `status`: Lọc theo status (scheduled, active, completed)

### POST /api/auction-sessions
Tạo phiên đấu giá mới (Admin only)

**Request Body:**
```json
{
  "title": "Đấu giá nhẫn kim cương",
  "description": "Phiên đấu giá đặc biệt...",
  "item_id": 1,
  "start_time": "2024-12-01T10:00:00Z",
  "end_time": "2024-12-01T12:00:00Z",
  "min_bid_increment": 1000000,
  "max_participants": 100
}
```

### GET /api/auction-sessions/active
Lấy phiên đấu giá đang diễn ra

### GET /api/auction-sessions/upcoming
Lấy phiên đấu giá sắp diễn ra

### POST /api/auction-sessions/{id}/join
Tham gia phiên đấu giá (Requires authentication)

---

## 💰 Bids Endpoints

### POST /api/bids
Đặt giá (Requires authentication + email verification)

**Request Body:**
```json
{
  "session_id": 1,
  "amount": 60000000
}
```

**Response:**
```json
{
  "success": true,
  "message": "Đặt giá thành công! Giá của bạn: 60,000,000 VND",
  "data": {
    "bid": {
      "id": 123,
      "amount": 60000000,
      "bid_time": "2024-01-01T10:30:00Z"
    },
    "new_highest_bid": 60000000,
    "next_minimum_bid": 61000000
  }
}
```

### GET /api/bids/session/{session_id}
Lấy lịch sử đặt giá của phiên

**Query Parameters:**
- `page`, `limit`: Pagination
- `order`: asc/desc (default: desc)

### GET /api/bids/my-bids
Lấy lịch sử đặt giá của user (Requires authentication)

### GET /api/bids/session/{session_id}/highest
Lấy giá cao nhất hiện tại

---

## 💳 Payments Endpoints

### GET /api/payments/methods
Lấy danh sách phương thức thanh toán

**Response:**
```json
{
  "success": true,
  "data": {
    "payment_methods": [
      {
        "id": "bank_transfer",
        "name": "Chuyển khoản ngân hàng",
        "fee_rate": 0.01,
        "processing_time": "1-2 ngày làm việc",
        "available": true
      }
    ],
    "recommended_method": "bank_transfer"
  }
}
```

### POST /api/payments/calculate-fees
Tính phí thanh toán

**Request Body:**
```json
{
  "amount": 60000000
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "original_amount": 60000000,
    "platform_fee": 3000000,
    "payment_fee": 1200000,
    "total_fees": 4200000,
    "net_amount": 55800000
  }
}
```

### GET /api/payments/my-payments
Lấy lịch sử thanh toán (Requires authentication)

---

## 📊 Error Handling

### Error Response Format
```json
{
  "success": false,
  "message": "Error message in Vietnamese",
  "errors": ["Detailed error 1", "Detailed error 2"],
  "data": null
}
```

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

### Common Error Messages
```json
{
  "401": "Token không được cung cấp",
  "403": "Bạn không có quyền truy cập",
  "404": "Không tìm thấy tài nguyên",
  "422": "Dữ liệu không hợp lệ",
  "500": "Lỗi hệ thống"
}
```

---

## 🔄 Pagination

Tất cả list endpoints đều support pagination:

**Request:**
```http
GET /api/auction-items?page=2&limit=10
```

**Response:**
```json
{
  "data": [...],
  "pagination": {
    "page": 2,
    "limit": 10,
    "total": 100,
    "pages": 10,
    "has_next": true,
    "has_prev": true
  }
}
```

---

## 🚀 Rate Limiting

- **Authentication endpoints**: 5 requests/minute
- **Bid endpoints**: 10 requests/minute
- **Other endpoints**: 100 requests/minute

---

## 📱 WebSocket Events

### Connection
```javascript
const socket = io('ws://127.0.0.1:5000');
```

### Events
- `bid_placed` - Có lượt đặt giá mới
- `auction_started` - Phiên đấu giá bắt đầu
- `auction_ending` - Phiên đấu giá sắp kết thúc
- `auction_ended` - Phiên đấu giá kết thúc

### Example
```javascript
socket.on('bid_placed', (data) => {
  console.log('New bid:', data.amount);
  // Update UI
});
```

---

## 🧪 Testing

### Postman Collection
Import collection từ: `/docs/postman_collection.json`

### Test Accounts
```
Admin: admin@auction.com / admin123
User: user@auction.com / user123
```

---

## 📞 Support

- **Email**: support@jewelry-auction.com
- **Documentation**: https://docs.jewelry-auction.com
- **GitHub**: https://github.com/jewelry-auction/api
