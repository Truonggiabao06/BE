# Đồ Án Hệ Thống Đấu Giá Trang Sức


## Mô tả đồ án
Em làm hệ thống đấu giá trang sức theo yêu cầu của thầy. Hệ thống có đầy đủ chức năng từ đăng ký, đăng nhập đến đấu giá và thanh toán.

## Chức năng đã làm được

### 1. Đăng ký, đăng nhập
- Đăng ký tài khoản mới
- Xác thực email bằng mã 6 số
- Đăng nhập với JWT token
- Phân quyền người dùng

### 2. Quản lý sản phẩm
- Đăng sản phẩm lên đấu giá
- Xem danh sách sản phẩm
- Tìm kiếm, lọc sản phẩm
- Phân loại theo danh mục

### 3. Quy trình định giá (mới)
- Nhân viên định giá sơ bộ
- Xác nhận nhận trang sức
- Định giá cuối cùng
- Quản lý duyệt/từ chối

### 4. Đấu giá
- Tạo phiên đấu giá
- Tham gia đấu giá
- Đặt giá theo thời gian thực
- Chống spam và cheat

### 5. Thanh toán
- Nhiều phương thức thanh toán
- Tính phí tự động
- Bảo vệ giao dịch
- Lịch sử thanh toán

### 6. Dashboard (mới)
- Dashboard cho nhân viên
- Dashboard cho quản lý
- Thống kê đơn giản
- Báo cáo cơ bản

### 7. Thông báo (mới)
- Thông báo trong hệ thống
- Đếm thông báo chưa đọc
- Gửi email thông báo

## Công nghệ sử dụng
- **Backend**: Python Flask
- **Database**: SQL Server
- **Authentication**: JWT
- **API**: RESTful API
- **Frontend**: React (dự định)

## Cách chạy project

### 1. Cài đặt
```bash
# Clone project
git clone [link]

# Cài đặt thư viện
pip install -r requirements.txt

# Cấu hình database trong .env
DATABASE_URL=your_database_url
JWT_SECRET_KEY=your_secret_key
```

### 2. Chạy server
```bash
python run.py
```

### 3. Test API
- Mở Postman
- Import file `postman_collection.json`
- Test các API endpoint

## API Endpoints chính

### Authentication
- `POST /api/auth/register` - Đăng ký
- `POST /api/auth/login` - Đăng nhập
- `POST /api/auth/verify-email` - Xác thực email

### Sản phẩm
- `GET /api/auction-items` - Danh sách sản phẩm
- `POST /api/auction-items` - Tạo sản phẩm mới
- `GET /api/auction-items/search` - Tìm kiếm

### Đấu giá
- `GET /api/auction-sessions` - Danh sách phiên đấu giá
- `POST /api/auction-sessions/{id}/join` - Tham gia đấu giá
- `POST /api/bids` - Đặt giá

### Nhân viên (mới)
- `GET /api/staff/items/pending` - Sản phẩm cần định giá
- `POST /api/staff/items/{id}/preliminary-valuation` - Định giá sơ bộ
- `POST /api/staff/items/{id}/final-valuation` - Định giá cuối cùng

### Quản lý (mới)
- `GET /api/manager/items/pending-approval` - Sản phẩm cần duyệt
- `POST /api/manager/items/{id}/approve` - Duyệt sản phẩm
- `GET /api/manager/fees` - Cấu hình phí

## Khó khăn gặp phải
1. **Database**: Ban đầu kết nối SQL Server gặp lỗi, em phải tìm hiểu thêm về connection string
2. **JWT**: Chưa hiểu rõ về JWT, phải học thêm từ internet
3. **Business Logic**: Quy trình đấu giá phức tạp, em tham khảo nhiều tài liệu
4. **API Design**: Thiết kế API RESTful chuẩn, học từ các tutorial online

## Tài liệu tham khảo
- Flask documentation
- SQLAlchemy tutorial
- JWT authentication guide
- RESTful API best practices
- Stack Overflow (nhiều câu hỏi)
- YouTube tutorials về Flask

## Kết quả đạt được
- ✅ Hoàn thành 100% yêu cầu cơ bản
- ✅ Bổ sung thêm quy trình định giá theo hình ảnh thầy gửi
- ✅ API hoạt động ổn định
- ✅ Database thiết kế hợp lý
- ✅ Code có comment và documentation

## Hướng phát triển
- Làm frontend với React
- Thêm WebSocket cho real-time
- Tối ưu performance
- Thêm unit test
- Deploy lên cloud

## Lời cảm ơn
Em cảm ơn thầy đã hướng dẫn và tạo điều kiện để em hoàn thành đồ án này. Qua đồ án em đã học được rất nhiều về lập trình web và thiết kế hệ thống.

---
**Ngày hoàn thành**: Tháng 8/2025
**Thời gian làm**: 2 tháng (tham khảo + code + test)
