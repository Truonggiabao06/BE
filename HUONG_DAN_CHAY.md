# Hướng Dẫn Chạy Đồ Án

## Chuẩn bị

### 1. Cài đặt Python
- Tải Python 3.8+ từ python.org
- Kiểm tra: `python --version`

### 2. Cài đặt thư viện
```bash
# Vào thư mục BE
cd BE

# Cài đặt requirements
pip install -r requirements.txt

# Nếu lỗi thì cài từng cái:
pip install flask
pip install flask-cors
pip install sqlalchemy
pip install pyodbc
pip install pyjwt
pip install bcrypt
```

### 3. Cấu hình Database
Tạo file `.env` trong thư mục BE:
```
DATABASE_URL=sqlite:///auction.db
JWT_SECRET_KEY=your-secret-key-here
EMAIL_SERVICE_API_KEY=test-key
FLASK_ENV=development
```

## Chạy Project

### 1. Khởi động server
```bash
# Trong thư mục BE
python run.py

# Hoặc dùng main.py
python main.py
```

Nếu thành công sẽ thấy:
```
* Running on http://127.0.0.1:5000
* Debug mode: on
```

### 2. Test API
```bash
# Test cơ bản
python test_simple.py
```

### 3. Mở trình duyệt
- Vào: http://127.0.0.1:5000
- Sẽ thấy thông tin API

## Test Chức Năng

### 1. Test Authentication
```bash
# Đăng ký (dùng Postman hoặc curl)
POST http://127.0.0.1:5000/api/auth/register
{
    "email": "test@example.com",
    "password": "123456",
    "full_name": "Test User"
}

# Đăng nhập
POST http://127.0.0.1:5000/api/auth/login
{
    "email": "test@example.com",
    "password": "123456"
}
```

### 2. Test Auction Items
```bash
# Xem sản phẩm
GET http://127.0.0.1:5000/api/auction-items

# Xem categories
GET http://127.0.0.1:5000/api/auction-items/categories
```

### 3. Test Workflow Mới
```bash
# Staff endpoints (cần token)
GET http://127.0.0.1:5000/api/staff/items/pending
GET http://127.0.0.1:5000/api/staff/dashboard

# Manager endpoints (cần token)
GET http://127.0.0.1:5000/api/manager/dashboard
GET http://127.0.0.1:5000/api/manager/fees
```

## Xử Lý Lỗi Thường Gặp

### 1. Lỗi import module
```
ModuleNotFoundError: No module named 'src'
```
**Giải pháp**: Chạy từ thư mục BE, không phải từ thư mục con

### 2. Lỗi database
```
sqlalchemy.exc.OperationalError
```
**Giải pháp**: Kiểm tra file .env và DATABASE_URL

### 3. Lỗi port đã sử dụng
```
Address already in use
```
**Giải pháp**: 
- Tắt process cũ: Ctrl+C
- Hoặc đổi port trong run.py

### 4. Lỗi CORS
```
Access-Control-Allow-Origin
```
**Giải pháp**: Đã cấu hình CORS, restart server

## Cấu Trúc Project

```
BE/
├── src/
│   ├── api/           # Controllers (API endpoints)
│   ├── application/   # Services (Business logic)
│   ├── domain/        # Models & Repositories
│   └── infrastructure/# Database & External services
├── run.py            # File chạy chính
├── requirements.txt  # Thư viện cần thiết
└── .env             # Cấu hình (tự tạo)
```

## Các File Quan Trọng

### 1. Controllers (API)
- `auth_controller.py` - Đăng ký, đăng nhập
- `auction_item_controller.py` - Quản lý sản phẩm
- `staff_controller.py` - API cho nhân viên (mới)
- `manager_controller.py` - API cho quản lý (mới)
- `dashboard_controller.py` - Dashboard (mới)

### 2. Models (Domain)
- `user.py` - Model người dùng
- `auction_item.py` - Model sản phẩm
- `fee_config.py` - Model cấu hình phí (mới)
- `notification.py` - Model thông báo (mới)

### 3. Services (Business Logic)
- `auction_service.py` - Logic đấu giá
- `valuation_service.py` - Logic định giá (mới)

## Demo Workflow

### 1. Quy trình cơ bản
1. Người dùng đăng ký → Xác thực email
2. Đăng sản phẩm → Trạng thái "pending_approval"
3. Nhân viên định giá sơ bộ → "preliminary_valued"
4. Nhân viên xác nhận nhận hàng → "item_received"
5. Nhân viên định giá cuối → "final_valued"
6. Quản lý duyệt → "approved"
7. Đưa lên đấu giá → "on_auction"

### 2. Test với Postman
- Import file `postman_collection.json`
- Chạy từng request theo thứ tự
- Xem response để hiểu workflow

## Lưu Ý

### 1. Code Style
- Em cố gắng viết code đơn giản, dễ hiểu
- Có comment tiếng Việt
- Một số chỗ chưa optimize (sẽ cải thiện sau)

### 2. Database
- Dùng SQLite cho đơn giản (file auction.db)
- Production có thể đổi sang SQL Server

### 3. Security
- JWT token có thời hạn
- Password được hash
- Validate input cơ bản

### 4. TODO
- [ ] Thêm unit test
- [ ] Optimize database queries  
- [ ] Thêm logging tốt hơn
- [ ] Frontend integration
- [ ] Deploy lên cloud

## Liên Hệ
Nếu có lỗi gì em sẽ fix thêm. Cảm ơn thầy đã hướng dẫn!
