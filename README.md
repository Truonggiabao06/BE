# Hệ thống quản lý đấu giá trang sức trực tuyến
I. Tổng quan dự án

# Mục tiêu

Mục tiêu của dự án là xây dựng một hệ thống đấu giá trang sức trực tuyến, nhằm kết nối người bán và người mua, đồng thời cung cấp cho công ty các công cụ để quản lý phiên đấu giá, sản phẩm và giao dịch một cách hiệu quả và minh bạch.

# Phạm vi

 Phạm vi dự án bao gồm các chức năng chính như: quản lý sản phẩm ký gửi, quản lý phiên đấu giá, quản lý người dùng (người bán, người mua, nhân viên), và quản lý giao dịch.

Việc tham gia đấu giá và đặt giá sẽ được thực hiện trực tuyến qua website, trong khi quy trình thẩm định giá và bàn giao sản phẩm sẽ được nhân viên thực hiện thủ công.

# Giả định và ràng buộc

* Hệ thống chỉ phục vụ cho hoạt động đấu giá trang sức của công ty, không phải là một sàn thương mại điện tử đa ngành hàng.

* Hệ thống quản lý các quy trình đấu giá và giao dịch, không phải là một phần mềm quản lý nhân sự hay kế toán chuyên sâu.

 * Hệ thống hỗ trợ ghi nhận trạng thái bàn giao sản phẩm, không tích hợp sâu với các đơn vị vận chuyển của bên thứ ba.

* Hệ thống có tích hợp cổng thanh toán cho việc giao dịch sản phẩm, không phải là một ví điện tử với đầy đủ chức năng nạp, rút, chuyển tiền.

#II. Yêu cầu chức năng

#  Các tác nhân 
* Guest (Khách vãng lai): Người dùng chưa đăng nhập.

* Seller (Người bán): Người dùng có tài khoản, thực hiện ký gửi trang sức để đấu giá.

* Buyer (Người mua): Người dùng có tài khoản, tham gia vào các phiên đấu giá.

* Staff (Nhân viên): Nhân viên của công ty, chịu trách nhiệm vận hành chính (định giá, quản lý phiên).

* Manager (Quản lý): Cấp quản lý, chịu trách nhiệm phê duyệt và giám sát.

* Admin (Quản trị viên): Người có quyền cao nhất, quản trị toàn bộ hệ thống.

# Code PlantUML

<img width="579" height="466" alt="image" src="https://github.com/user-attachments/assets/bf19396d-a911-4d20-a629-2cfa38de5c65" />

# Các chức năng chính

#  Guest:

* Xem sản phẩm/phiên đấu giá: Cho phép xem danh sách các sản phẩm và các phiên đấu giá đang diễn ra hoặc sắp tới.

* Tìm kiếm sản phẩm: Cho phép người dùng tìm kiếm sản phẩm dựa trên tên, loại trang sức, khoảng giá khởi điểm...

* Xem thông tin chi tiết sản phẩm: Hiển thị đầy đủ thông tin của một sản phẩm, bao gồm mô tả, chất liệu, hình ảnh, video, giá khởi điểm, và lịch sử các mức giá đã được đặt (nếu phiên đang diễn ra).

* Đăng ký: Tạo tài khoản mới để có thể tham gia với vai trò người mua hoặc người bán.

* Đăng nhập: Đăng nhập vào hệ thống bằng tài khoản đã đăng ký.

# Buyer & Seller:
* Quản lý tài khoản: Cập nhật thông tin cá nhân, thay đổi mật khẩu, quản lý địa chỉ và thông tin thanh toán.

* Tạo yêu cầu ký gửi (Seller): Điền form để gửi yêu cầu đấu giá cho sản phẩm của mình, bao gồm mô tả, hình ảnh và giá mong muốn.

* Theo dõi sản phẩm (Seller): Xem trạng thái các sản phẩm đã ký gửi (chờ duyệt, đã định giá, đang đấu giá, đã bán).

* Đăng ký tham gia phiên (Buyer): Đăng ký để có quyền tham gia và đặt giá trong một phiên đấu giá cụ thể.

* Đặt giá (Buyer): Thực hiện đặt giá cho sản phẩm mong muốn trong thời gian phiên đấu giá diễn ra.

* Lịch sử giao dịch: Xem lại lịch sử các sản phẩm đã bán (đối với Seller) hoặc lịch sử các phiên đã tham gia và các sản phẩm đã thắng (đối với Buyer).

* Thanh toán (Buyer): Thực hiện thanh toán trực tuyến cho sản phẩm đã thắng cuộc.

# Staff:
* Quản lý sản phẩm: Tiếp nhận yêu cầu ký gửi, thẩm định chất lượng, cập nhật thông tin chi tiết và hình ảnh cho sản phẩm.

* Quản lý phiên đấu giá:

* Tạo phiên: Lên lịch phiên đấu giá mới, ấn định thời gian, thêm sản phẩm vào phiên.

* Vận hành phiên: Bắt đầu, tạm dừng, hoặc kết thúc một phiên đấu giá.

* Quản lý giao dịch: Xác nhận thanh toán thành công từ người mua và cập nhật trạng thái để tiến hành bàn giao sản phẩm.

* Hỗ trợ người dùng: Xem và phản hồi các yêu cầu hỗ trợ từ người dùng.

# Manager:
* Phê duyệt giá: Xem xét và phê duyệt mức giá khởi điểm cuối cùng do nhân viên đề xuất cho các sản phẩm quan trọng.

* Quản lý nhân viên: Xem danh sách nhân viên và hiệu suất làm việc.

* Xem báo cáo: Truy cập các báo cáo thống kê về doanh thu, số lượng sản phẩm, hiệu quả của các phiên đấu giá.

* Quản lý phí và hoa hồng: Cấu hình các mức phí giao dịch áp dụng cho người mua và người bán.

# Admin:

* Quản lý tài khoản: Có toàn quyền xem, tạo, sửa, xóa, khóa/mở khóa tài khoản của tất cả người dùng trong hệ thống.

* Giám sát hệ thống: Theo dõi toàn bộ hoạt động, lịch sử giao dịch, và các log hệ thống để đảm bảo an ninh và ổn định.

* Cấu hình hệ thống: Quản lý các cài đặt chung, các quy định, và các tham số cốt lõi của website.

## Biểu đồ Use Case



<details>
<summary> Code plantUML</summary>

```plantuml
@startuml
' === Cài đặt giao diện cho giống ví dụ ===
!theme plain
skinparam defaultTextAlignment center
skinparam actor {
    borderColor black
    backgroundColor white
}
skinparam rectangle {
    borderColor black
    backgroundColor white
}
skinparam package {
    borderColor gray
    backgroundColor white
}
skinparam usecase {
    borderColor black
    backgroundColor white
}
skinparam arrow {
    color black
}

title Biểu đồ Use Case - Hệ thống Đấu giá Trang sức

actor Guest as "Khách vãng lai"
actor Customer as "Khách hàng\n(Mua/Bán)"
actor Staff as "Nhân viên"
actor Manager as "Quản lý"

rectangle "Hệ thống" {
    package "Chức năng Khách hàng" as PCustomer {
        usecase "Quản lý tài khoản" as UC_Profile
        usecase "Tạo yêu cầu ký gửi" as UC_Consign
        usecase "Đặt giá" as UC_Bid
        usecase "Thanh toán" as UC_Pay
    }
    
    package "Chức năng Guest" as PGuest {
        usecase "Xem sản phẩm" as UC_View
        usecase "Tìm kiếm" as UC_Search
        usecase "Đăng nhập" as UC_Login
        usecase "Đăng ký" as UC_Register
    }
    
    package "Chức năng Nhân viên" as PStaff {
        usecase "Quản lý sản phẩm" as UC_ManageProducts
        usecase "Quản lý phiên đấu giá" as UC_ManageSessions
        usecase "Xác nhận giao dịch" as UC_Confirm
    }

    package "Chức năng Quản lý" as PManager {
        usecase "Phê duyệt giá" as UC_Approve
        usecase "Xem báo cáo" as UC_Report
        usecase "Quản lý người dùng" as UC_ManageUsers
    }

    PCustomer -[hidden]down- PGuest
    PStaff -[hidden]down- PManager
    PGuest -[hidden]right- PManager
}

Guest --> UC_View
Guest --> UC_Search
Guest --> UC_Login
Guest --> UC_Register

Customer --> UC_Profile
Customer --> UC_Consign
Customer --> UC_Bid
Customer --> UC_Pay

Staff --> UC_ManageProducts
Staff --> UC_ManageSessions
Staff --> UC_Confirm

Manager --> UC_Approve
Manager --> UC_Report
Manager --> UC_ManageUsers

Customer --|> Guest
Manager --|> Staff

Guest -[hidden]left- PGuest
Customer -[hidden]left- PCustomer
Staff -[hidden]right- PStaff
Manager -[hidden]right- PManager
@enduml

</details>



<img width="1518" height="511" alt="Ảnh chụp màn hình 2025-08-12 011929" src="https://github.com/user-attachments/assets/fbbfe5dd-01e4-4342-9beb-8bfd47fbff0c" />


