# 🏺 HƯỚNG DẪN CÀI ĐẶT VÀ CHẠY DỰ ÁN JEWELRY AUCTION

## 📋 **MÔ TẢ DỰ ÁN**

Hệ thống đấu giá trang sức trực tuyến được xây dựng theo kiến trúc Clean Architecture với Flask và SQL Server.

### **🎯 Tính năng chính:**
- 🔐 Xác thực và phân quyền người dùng (JWT)
- 💎 Quản lý trang sức và yêu cầu bán
- 🏛️ Tạo và quản lý phiên đấu giá
- 💰 Hệ thống đặt giá thầu
- 📄 Tài liệu API tự động (Swagger)
- 🐳 Hỗ trợ Docker deployment

## 🛠️ **YÊU CẦU HỆ THỐNG**

### **Phần mềm cần thiết:**
- **Python 3.11+** 
- **SQL Server 2022+** (hoặc Docker container)
- **Git** để clone dự án
- **Docker Desktop** (tùy chọn)

### **Kiến thức cần có:**
- Cơ bản về Python và Flask
- Hiểu biết về REST API
- Cơ bản về SQL Server

## 📥 **BƯỚC 1: TẢI VÀ CÀI ĐẶT**

### **1.1 Clone dự án:**
```bash
git clone <repository-url>
cd "JEWELRY AUCTION"
```

### **1.2 Tạo môi trường ảo:**
```bash
# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### **1.3 Cài đặt dependencies:**
```bash
pip install -r requirements.txt
```

## 🗄️ **BƯỚC 2: CÀI ĐẶT DATABASE**

### **2.1 Sử dụng Docker (Khuyến nghị):**
```bash
# Tạo SQL Server container
docker run -e "ACCEPT_EULA=Y" -e "MSSQL_SA_PASSWORD=Aa@123456" \
  -p 1433:1433 --name sql1 --hostname sql1 \
  -d mcr.microsoft.com/mssql/server:latest

# Kiểm tra container đang chạy
docker ps
```

### **2.2 Hoặc cài đặt SQL Server trực tiếp:**
- Tải SQL Server Developer Edition
- Cài đặt với SA password: `Aa@123456`
- Đảm bảo SQL Server chạy trên port 1433

## ⚙️ **BƯỚC 3: CẤU HÌNH DỰ ÁN**

### **3.1 Kiểm tra file cấu hình:**
File `src/config.py` đã được cấu hình sẵn:
```python
DB_URL = 'mssql+pyodbc://sa:Giabao06%40@localhost:1433/jewelry_auction_dev?driver=ODBC+Driver+17+for+SQL+Server'
```

### **3.2 Tạo database và seed data:**
```bash
cd src
python scripts/seeds.py
```

## 🚀 **BƯỚC 4: CHẠY ỨNG DỤNG**

### **4.1 Khởi động API:**
```bash
cd src
python app.py
```

### **4.2 Kiểm tra ứng dụng:**
- **API Base URL**: http://127.0.0.1:5000
- **Health Check**: http://127.0.0.1:5000/health
- **API Documentation**: http://127.0.0.1:5000/api/docs
- **Swagger UI**: Giao diện tương tác với API

## 👥 **TÀI KHOẢN DEMO**

Sau khi chạy seed data, bạn có thể sử dụng các tài khoản sau:

| Vai trò | Email | Mật khẩu | Quyền hạn |
|---------|-------|----------|-----------|
| **Admin** | admin@example.com | Admin@123 | Toàn quyền hệ thống |
| **Manager** | manager@example.com | Manager@123 | Duyệt yêu cầu, quản lý phiên |
| **Staff** | staff@example.com | Staff@123 | Tạo trang sức, quản lý |
| **Member** | member@example.com | Member@123 | Bán trang sức, đấu giá |

## 🧪 **BƯỚC 5: KIỂM THỬ API**

### **5.1 Test tự động:**
```bash
cd src
python scripts/test_api.py
```

### **5.2 Test thủ công:**
1. Mở Swagger UI: http://127.0.0.1:5000/api/docs
2. Đăng nhập với tài khoản demo
3. Copy JWT token từ response
4. Sử dụng token để test các endpoint khác

## 🐳 **CHẠY VỚI DOCKER (TÙY CHỌN)**

### **Sử dụng Docker Compose:**
```bash
# Build và chạy tất cả services
docker-compose up --build -d

# Xem logs
docker-compose logs -f app

# Dừng services
docker-compose down
```

## 🔧 **XỬ LÝ SỰ CỐ**

### **Lỗi thường gặp:**

**1. Không kết nối được database:**
```bash
# Kiểm tra SQL Server container
docker ps
docker start sql1

# Hoặc restart container
docker restart sql1
```

**2. Lỗi import module:**
```bash
# Đảm bảo đang ở đúng thư mục
cd src
python app.py
```

**3. Port 5000 đã được sử dụng:**
```bash
# Tìm và kill process đang dùng port 5000
netstat -ano | findstr :5000
taskkill /PID <PID_NUMBER> /F
```

## 📚 **TÀI LIỆU THAM KHẢO**

- **API Documentation**: Xem file `NEW_ENDPOINTS.md`
- **Architecture**: Xem file `docs/flask-clean-architecture.md`
- **Postman Collection**: Sử dụng file trong `src/postman/`

## 🎯 **DEMO CHO GIẢNG VIÊN**

### **Các bước demo:**
1. ✅ Khởi động SQL Server container
2. ✅ Chạy Flask API
3. ✅ Mở Swagger documentation
4. ✅ Demo đăng nhập với các role khác nhau
5. ✅ Test CRUD operations
6. ✅ Giải thích Clean Architecture

### **Điểm nổi bật để trình bày:**
- 🏗️ **Clean Architecture**: Tách biệt rõ ràng các layer
- 🔐 **Security**: JWT authentication, role-based access
- 📊 **Database**: SQL Server với DECIMAL cho tiền tệ
- 🧪 **Testing**: Comprehensive test suite
- 📖 **Documentation**: Auto-generated API docs
- 🐳 **DevOps**: Docker containerization ready

---

**🎉 Chúc bạn thành công với dự án!**
