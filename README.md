# Hệ thống quản lý đấu giá trang sức trực tuyến
# I. Tổng quan dự án

## Mục tiêu

Mục tiêu của dự án là xây dựng một hệ thống đấu giá trang sức trực tuyến, nhằm kết nối người bán và người mua, đồng thời cung cấp cho công ty các công cụ để quản lý phiên đấu giá, sản phẩm và giao dịch một cách hiệu quả và minh bạch.

## Phạm vi

 Phạm vi dự án bao gồm các chức năng chính như: quản lý sản phẩm ký gửi, quản lý phiên đấu giá, quản lý người dùng (người bán, người mua, nhân viên), và quản lý giao dịch.

Việc tham gia đấu giá và đặt giá sẽ được thực hiện trực tuyến qua website, trong khi quy trình thẩm định giá và bàn giao sản phẩm sẽ được nhân viên thực hiện thủ công.

## Giả định và ràng buộc

* Hệ thống chỉ phục vụ cho hoạt động đấu giá trang sức của công ty, không phải là một sàn thương mại điện tử đa ngành hàng.

* Hệ thống quản lý các quy trình đấu giá và giao dịch, không phải là một phần mềm quản lý nhân sự hay kế toán chuyên sâu.

 * Hệ thống hỗ trợ ghi nhận trạng thái bàn giao sản phẩm, không tích hợp sâu với các đơn vị vận chuyển của bên thứ ba.

* Hệ thống có tích hợp cổng thanh toán cho việc giao dịch sản phẩm, không phải là một ví điện tử với đầy đủ chức năng nạp, rút, chuyển tiền.

# II. Yêu cầu chức năng

##  Các tác nhân 
* Guest (Khách vãng lai): Người dùng chưa đăng nhập.

* Seller (Người bán): Người dùng có tài khoản, thực hiện ký gửi trang sức để đấu giá.

* Buyer (Người mua): Người dùng có tài khoản, tham gia vào các phiên đấu giá.

* Staff (Nhân viên): Nhân viên của công ty, chịu trách nhiệm vận hành chính (định giá, quản lý phiên).

* Manager (Quản lý): Cấp quản lý, chịu trách nhiệm phê duyệt và giám sát.

* Admin (Quản trị viên): Người có quyền cao nhất, quản trị toàn bộ hệ thống.


<details>
<summary> Code PlantUML</summary>

```plantuml
@startuml
!theme plain
skinparam shadowing false
skinparam defaultTextAlignment center
skinparam actor {
    borderColor black
    backgroundColor white
}
skinparam rectangle {
    borderColor black
    backgroundColor white
}


rectangle "Hệ thống\nĐấu giá" as System

actor Guest as "Khách vãng lai"
actor Customer as "Khách hàng"
actor Staff as "Nhân viên"
actor Manager as "Quản lý"
actor Admin as "Quản trị viên"





Guest --> System : truy cập
Customer --> System : sử dụng
Staff --> System : vận hành
Manager --> System : quản lý
Admin --> System : quản trị



Customer --|> Guest
Manager --> Staff : quản lý
Admin --> Manager : quản lý

@enduml
```
</details>

<img width="579" height="466" alt="image" src="https://github.com/user-attachments/assets/bf19396d-a911-4d20-a629-2cfa38de5c65" />

## Các chức năng chính

###  Guest:

* Xem sản phẩm/phiên đấu giá: Cho phép xem danh sách các sản phẩm và các phiên đấu giá đang diễn ra hoặc sắp tới.

* Tìm kiếm sản phẩm: Cho phép người dùng tìm kiếm sản phẩm dựa trên tên, loại trang sức, khoảng giá khởi điểm...

* Xem thông tin chi tiết sản phẩm: Hiển thị đầy đủ thông tin của một sản phẩm, bao gồm mô tả, chất liệu, hình ảnh, video, giá khởi điểm, và lịch sử các mức giá đã được đặt (nếu phiên đang diễn ra).

* Đăng ký: Tạo tài khoản mới để có thể tham gia với vai trò người mua hoặc người bán.

* Đăng nhập: Đăng nhập vào hệ thống bằng tài khoản đã đăng ký.

### Buyer & Seller:
* Quản lý tài khoản: Cập nhật thông tin cá nhân, thay đổi mật khẩu, quản lý địa chỉ và thông tin thanh toán.

* Tạo yêu cầu ký gửi (Seller): Điền form để gửi yêu cầu đấu giá cho sản phẩm của mình, bao gồm mô tả, hình ảnh và giá mong muốn.

* Theo dõi sản phẩm (Seller): Xem trạng thái các sản phẩm đã ký gửi (chờ duyệt, đã định giá, đang đấu giá, đã bán).

* Đăng ký tham gia phiên (Buyer): Đăng ký để có quyền tham gia và đặt giá trong một phiên đấu giá cụ thể.

* Đặt giá (Buyer): Thực hiện đặt giá cho sản phẩm mong muốn trong thời gian phiên đấu giá diễn ra.

* Lịch sử giao dịch: Xem lại lịch sử các sản phẩm đã bán (đối với Seller) hoặc lịch sử các phiên đã tham gia và các sản phẩm đã thắng (đối với Buyer).

* Thanh toán (Buyer): Thực hiện thanh toán trực tuyến cho sản phẩm đã thắng cuộc.

### Staff:
* Quản lý sản phẩm: Tiếp nhận yêu cầu ký gửi, thẩm định chất lượng, cập nhật thông tin chi tiết và hình ảnh cho sản phẩm.

* Quản lý phiên đấu giá:

* Tạo phiên: Lên lịch phiên đấu giá mới, ấn định thời gian, thêm sản phẩm vào phiên.

* Vận hành phiên: Bắt đầu, tạm dừng, hoặc kết thúc một phiên đấu giá.

* Quản lý giao dịch: Xác nhận thanh toán thành công từ người mua và cập nhật trạng thái để tiến hành bàn giao sản phẩm.

* Hỗ trợ người dùng: Xem và phản hồi các yêu cầu hỗ trợ từ người dùng.

### Manager:
* Phê duyệt giá: Xem xét và phê duyệt mức giá khởi điểm cuối cùng do nhân viên đề xuất cho các sản phẩm quan trọng.

* Quản lý nhân viên: Xem danh sách nhân viên và hiệu suất làm việc.

* Xem báo cáo: Truy cập các báo cáo thống kê về doanh thu, số lượng sản phẩm, hiệu quả của các phiên đấu giá.

* Quản lý phí và hoa hồng: Cấu hình các mức phí giao dịch áp dụng cho người mua và người bán.

### Admin:

* Quản lý tài khoản: Có toàn quyền xem, tạo, sửa, xóa, khóa/mở khóa tài khoản của tất cả người dùng trong hệ thống.

* Giám sát hệ thống: Theo dõi toàn bộ hoạt động, lịch sử giao dịch, và các log hệ thống để đảm bảo an ninh và ổn định.

* Cấu hình hệ thống: Quản lý các cài đặt chung, các quy định, và các tham số cốt lõi của website.

# Biểu đồ Use Case

<details>
<summary> Code PlantUML</summary>

```plantuml
@startuml "Biểu đồ Use Case tổng quan" 

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
```
</details>



 <img width="1518" height="511" alt="Ảnh chụp màn hình 2025-08-12 011929" src="https://github.com/user-attachments/assets/07c216b0-8636-4ac1-bea4-d63c81d613e0" />


# Biểu đồ Use Case chi tiết
## Chữc năng Guest
<details>
<summary> Code PlantUML</summary>

```plantuml
@startuml
!theme plain
left to right direction

actor Guest as "Khách mời"

rectangle "Hệ thống" {
    usecase "Xem sản phẩm / phiên" as UC1
    usecase "Tìm kiếm sản phẩm" as UC2
    usecase "Xem thông tin chi tiết" as UC3
    usecase "Đăng ký" as UC4
    usecase "Đăng nhập" as UC5
}

Guest --> UC1
Guest --> UC2
Guest --> UC3
Guest --> UC4
Guest --> UC5
@enduml
```
</details>
<img width="338" height="376" alt="image" src="https://github.com/user-attachments/assets/da363b48-ce0a-4d27-9df2-5ed72828e053" />

## Chức năng Buyer
<details>
<summary> Code PlantUML</summary>

```plantuml
@startuml
!theme plain
left to right direction

actor Buyer as "Người mua"

rectangle "Hệ thống" {
    usecase "Quản lý tài khoản" as UC1
    usecase "Xem lịch sử giao dịch" as UC2
    usecase "Đăng ký tham gia phiên" as UC3
    usecase "Đặt giá" as UC4
    usecase "Thanh toán" as UC5
}

Buyer --> UC1
Buyer --> UC2
Buyer --> UC3
Buyer --> UC4
Buyer --> UC5
@enduml
```
</details>
<img width="349" height="377" alt="image" src="https://github.com/user-attachments/assets/e7158784-fdf5-4eba-9678-f0909956a95f" />

## Chức năng Seller
<details>
<summary> Code PlantUML</summary>

```plantuml
@startuml
!theme plain
left to right direction

actor Seller as "Người bán"

rectangle "Hệ thống" {
    usecase "Quản lý tài khoản" as UC1
    usecase "Xem lịch sử giao dịch" as UC2
    usecase "Tạo yêu cầu ký gửi" as UC3
    usecase "Theo dõi sản phẩm" as UC4
}

Seller --> UC1
Seller --> UC2
Seller --> UC3
Seller --> UC4
@enduml
```
</details>
<img width="346" height="318" alt="image" src="https://github.com/user-attachments/assets/78ff4f64-8b03-4258-ae08-d70ebc651dc4" />

## Chức năng Staff
<details>
<summary> Code PlantUML</summary>

```plantum
@startuml
!theme plain
left to right direction

actor Staff as "Nhân viên"

rectangle "Hệ thống" {
    usecase "Quản lý sản phẩm" as UC1
    usecase "Quản lý phiên đấu giá" as UC2
    usecase "Tạo phiên" as UC3
    usecase "Vận hành phiên" as UC4
    usecase "Quản lý giao dịch" as UC5
    usecase "Hỗ trợ người dùng" as UC6
}

Staff --> UC1
Staff --> UC2
Staff --> UC3
Staff --> UC4
Staff --> UC5
Staff --> UC6
@enduml

```
</details>
<img width="382" height="522" alt="image" src="https://github.com/user-attachments/assets/2c4b1532-bdaf-492d-a583-f740c31f87f0" />


## Chức năng Manager
<details>
<summary> Code PlantUML</summary>

```plantum
@startuml
!theme plain
left to right direction

actor Manager as "Giám đốc"

rectangle "Hệ thống" {
    usecase "Phê duyệt giá" as UC1
    usecase "Quản lý nhân viên" as UC2
    usecase "Xem báo cáo" as UC3
    usecase "Quản lý phí & hoa hồng" as UC4
}

Manager --> UC1
Manager --> UC2
Manager --> UC3
Manager --> UC4
@enduml
```
</details>
<img width="359" height="308" alt="image" src="https://github.com/user-attachments/assets/bbe1fba7-3a0d-4065-8689-166143b28d7c" />

## Chức năng Admin
<details>
<summary> Code PlantUML</summary>

```plantum
@startuml
!theme plain
left to right direction

actor Admin as "Quản trị viên"

rectangle "Hệ thống" {
    usecase "Quản lý tài khoản người dùng" as UC1
    usecase "Giám sát hệ thống" as UC2
    usecase "Cấu hình hệ thống" as UC3
}

Admin --> UC1
Admin --> UC2
Admin --> UC3
@enduml
```
</details>
<img width="410" height="256" alt="image" src="https://github.com/user-attachments/assets/b6a824dd-85b9-4c2f-a30a-e91d6d7368f9" />

# Quy trình hoạt động
## Quy trình ký gửi sản phẩm


* Người bán: Đăng nhập vào hệ thống và chọn chức năng "Tạo yêu cầu ký gửi".

* Người bán: Điền đầy đủ thông tin mô tả sản phẩm, tải lên hình ảnh chi tiết và gửi yêu cầu.

* Hệ thống: Tiếp nhận yêu cầu, lưu trữ với trạng thái "Chờ duyệt" và tạo một thông báo mới cho các Nhân viên liên quan.

* Nhân viên: Truy cập danh sách các yêu cầu đang chờ, chọn một yêu cầu để bắt đầu quá trình thẩm định.

* Nhân viên: Dựa trên thông tin và hình ảnh, thực hiện thẩm định, đề xuất mức giá khởi điểm và cập nhật vào hệ thống.

* Nhân viên: Với các sản phẩm có giá trị cao, Nhân viên sẽ trình yêu cầu lên cho Giám đốc.

* Giám đốc: Xem xét yêu cầu, kiểm tra thông tin thẩm định và mức giá khởi điểm.

* Giám đốc: Thực hiện Phê duyệt hoặc Từ chối yêu cầu.

* Hệ thống: Cập nhật trạng thái cuối cùng cho sản phẩm .

* Hệ thống: Tự động gửi một thông báo (notification) đến Người bán về kết quả của yêu cầu ký gửi.


<details>
<summary> Code PlantUML</summary>

```plantum
@startuml
!theme plain
title Quy trình Ký gửi Sản phẩm

|Người bán|
start
:Đăng nhập & chọn "Tạo yêu cầu ký gửi";
:Điền thông tin & Gửi yêu cầu;

|Hệ thống|
:Tiếp nhận yêu cầu;
:Đặt trạng thái = "Chờ duyệt";
:Thông báo cho Nhân viên;

|Nhân viên|
:Tiếp nhận yêu cầu;
:Thẩm định & đề xuất giá khởi điểm;

if (Sản phẩm giá trị cao?) then (yes)
  :Trình yêu cầu lên Giám đốc;

  |Giám đốc|
  :Xem xét hồ sơ & Kiểm tra thông tin;
  if (Phê duyệt?) then (Duyệt)
    |Hệ thống|
    :Cập nhật trạng thái = "Sẵn sàng đấu giá";
  else (Từ chối)
    |Hệ thống|
    :Cập nhật trạng thái = "Bị từ chối";
  endif

else (no)
  |Hệ thống|
  :Cập nhật trạng thái = "Sẵn sàng đấu giá";
endif

|Hệ thống|
:Thông báo kết quả cho Nhân viên & Người bán;

|Người bán|
stop
@enduml
```
</details>
<img width="1281" height="646" alt="image" src="https://github.com/user-attachments/assets/7084d54a-174a-4b3b-8d97-7303a20876f4" />

## Quy trình tham gia đấu giá
* Người mua: Đăng nhập và truy cập vào danh sách các phiên đấu giá đang hoặc sắp diễn ra.

* Người mua: Chọn một phiên đấu giá cụ thể và nhấn "Đăng ký tham gia".

* Hệ thống: Ghi nhận việc đăng ký và cho phép Người mua truy cập vào phòng đấu giá khi phiên bắt đầu.

* Hệ thống: Khi phiên đấu giá bắt đầu, hệ thống hiển thị sản phẩm, giá cao nhất hiện tại và đồng hồ đếm ngược.

* Người mua: Nhập mức giá mong muốn (phải cao hơn giá hiện tại + bước giá tối thiểu) và nhấn nút "Đặt giá".

* Hệ thống: Xác thực mức giá.

* Nếu hợp lệ: Ghi nhận mức giá mới, cập nhật lại thông tin "giá cao nhất" và "người giữ giá" trên giao diện của tất cả người dùng trong phiên.

* Nếu không hợp lệ: Hiển thị thông báo lỗi cho Người mua.

* Hệ thống: Khi đồng hồ đếm ngược kết thúc, hệ thống sẽ chốt phiên cho sản phẩm đó.

* Hệ thống: Tự động xác định người giữ giá cuối cùng là người thắng cuộc.

* Hệ thống: Gửi thông báo thắng cuộc đến cho Người mua và tạo một giao dịch mới đang chờ thanh toán.

<details>
<summary> Code PlantUML</summary>

```plantum
@startuml
!theme plain
title Quy trình Tham gia và Đấu giá

|Người mua|
start
:Đăng nhập & Tìm phiên đấu giá;
:Đăng ký tham gia phiên;

|Hệ thống|
:Tiếp nhận đăng ký;
:Cho phép truy cập "phòng đấu giá"\nkhi phiên bắt đầu;
:Đến thời điểm bắt đầu → Khởi tạo phiên & đếm ngược;

while (Còn thời gian?) is (yes)
  :Hiển thị sản phẩm,\nGiá cao nhất & Người giữ giá,\nThời gian còn lại;

  |Người mua|
  :Nhập mức giá >=\nGiá hiện tại + Bước tối thiểu;
  :Nhấn "Đặt giá";

  |Hệ thống|
  if (Giá đặt hợp lệ?) then (yes)
    :Ghi nhận giá mới;
    :Cập nhật "Giá cao nhất"\n& "Người giữ giá";
    :Broadcast cập nhật\nreal-time cho tất cả;
  else (no)
    :Thông báo lỗi cho Người mua;
  endif
endwhile (no)

: Xác định người thắng cuộc\n= Người giữ giá cuối cùng;
: Tạo "Giao dịch mới"\ntrạng thái "Chờ thanh toán";
: Gửi thông báo thắng cuộc\ncho Người mua;

|Người mua|
stop
@enduml
```
</details>
<img width="412" height="730" alt="image" src="https://github.com/user-attachments/assets/6a244bee-88b8-4f9f-a658-3d6e79be46cd" />

## Quy trình Thanh toán và Hoàn tất Giao dịch

* Người mua: Nhận được thông báo thắng cuộc và truy cập vào mục "Giao dịch của tôi".

* Người mua: Chọn giao dịch đang chờ và nhấn "Tiến hành thanh toán".

* Hệ thống: Chuyển hướng người dùng đến một cổng thanh toán an toàn của bên thứ ba.

* Người mua: Nhập thông tin và hoàn tất việc thanh toán trên cổng thanh toán.

* Hệ thống: Nhận tín hiệu xác nhận thanh toán thành công từ cổng thanh toán.

* Hệ thống: Cập nhật trạng thái giao dịch thành "Đã thanh toán" và gửi thông báo cho Nhân viên.

* Nhân viên: Nhận thông báo, chuẩn bị sản phẩm và liên hệ với Người mua để sắp xếp việc bàn giao.

* Nhân viên: Sau khi bàn giao sản phẩm thành công, Nhân viên cập nhật trạng thái cuối cùng của giao dịch thành "Đã hoàn tất".

* Hệ thống: Ghi nhận giao dịch đã kết thúc thành công. Dựa trên đó, hệ thống sẽ tính toán và lên lịch chuyển tiền cho Người bán sau khi đã trừ đi các khoản phí dịch vụ.

<details>
<summary> Code PlantUML</summary>

```plantum
@startuml
!theme plain
skinparam defaultFontName Arial
title Quy trình Thanh toán và Hoàn tất Giao dịch

|Hệ thống|
start
: Tạo giao dịch "Chờ thanh toán";
: Gửi thông báo thắng cuộc cho Người mua;

|Người mua|
: Mở "Giao dịch của tôi";
: Chọn giao dịch đang chờ và nhấn "Thanh toán";

|Hệ thống|
: Chuyển hướng sang cổng thanh toán;

|Cổng thanh toán|
: Hiển thị form thanh toán;
: Người mua nhập thông tin & xác nhận;
: Xử lý giao dịch;

|Hệ thống|
: Nhận kết quả từ cổng thanh toán;
if (Thanh toán thành công?) then (Yes)
  : Cập nhật trạng thái = "Đã thanh toán";
  : Thông báo cho Nhân viên;

  |Nhân viên|
  : Chuẩn bị sản phẩm & liên hệ bàn giao;
  : Bàn giao sản phẩm;
  : Cập nhật trạng thái cuối = "Đã hoàn tất";

  |Hệ thống|
  : Ghi nhận giao dịch đã kết thúc;
  : Tính phí dịch vụ & số tiền chuyển;
  : Lên lịch chuyển tiền cho Người bán;
  stop
else (No)
  : Ghi nhận lỗi thanh toán;
  : Thông báo thanh toán thất bại cho Người mua;
  stop
endif
@enduml

```
</details>
<img width="1118" height="857" alt="image" src="https://github.com/user-attachments/assets/c8564872-bd98-4a34-b680-4445b45c81c3" />


# Luồng xử lý
## Luồng xử lý đăng lý

<details>
<summary> Code PlantUML</summary>

```plantum
@startuml "Biểu đồ trình tự đăng ký"
!theme plain
autonumber "<b>[0]"

actor "Khách" as guest
participant "Giao diện" as ui
participant "Hệ thống" as system
database "CSDL" as db

guest -> ui: Truy cập form đăng ký
activate ui

guest -> ui: Điền thông tin\n(họ tên, email, SĐT, mật khẩu)
ui -> system: Gửi thông tin đăng ký

activate system
system -> system: Kiểm tra tính hợp lệ của thông tin
alt Thông tin hợp lệ
    system -> db: Lưu thông tin tài khoản 
    activate db
    db --> system: Xác nhận lưu thành công
    deactivate db

    system -> system: Tạo mã xác thực email
    system -> guest: Gửi email chứa link xác thực
    system --> ui: Thông báo đăng ký thành công
    ui --> guest: Chuyển đến trang hướng dẫn xác thực
else Thông tin không hợp lệ
    system --> ui: Trả về lỗi
    ui --> guest: Hiển thị thông báo lỗi
end
deactivate system
deactivate ui
@enduml
```
</details>
<img width="952" height="621" alt="image" src="https://github.com/user-attachments/assets/6b1acbb2-d256-435c-85db-2ebae9c6f74f" />

## Luồng xử lý Đăng nhập

<details>
<summary> Code PlantUML</summary>

```plantum
@startuml "Biểu đồ trình tự đăng nhập"
!theme plain
autonumber "<b>[0]"

actor "Người dùng" as user
participant "Giao diện" as ui
participant "Hệ thống" as system
database "CSDL" as db

user -> ui: Điền email, mật khẩu & nhấn Đăng nhập
activate ui
ui -> system: Gửi thông tin đăng nhập

activate system
system -> db: Tìm người dùng theo email
activate db
db --> system: Trả về thông tin tài khoản
deactivate db

system -> system: So sánh mật khẩu
alt Mật khẩu chính xác
    system -> system: Kiểm tra trạng thái tài khoản
    
    alt Tài khoản đã xác thực
        system -> system: Tạo JWT Token
        system --> ui: Trả về Token & thông tin người dùng
        ui --> user: Đăng nhập thành công & chuyển trang
    else Tài khoản chưa xác thực
        system --> ui: Trả về lỗi "Tài khoản chưa xác thực"
        ui --> user: Hiển thị thông báo yêu cầu xác thực email
    end
else Mật khẩu không chính xác
    system --> ui: Trả về lỗi "Sai thông tin đăng nhập"
    ui --> user: Hiển thị thông báo lỗi
end
deactivate system
deactivate ui
@enduml
```
</details>

<img width="834" height="577" alt="image" src="https://github.com/user-attachments/assets/6a89845f-4555-4cc9-9414-508e57ab5c08" />


## Luồng xử lý Đặt giá

<details>
<summary> Code PlantUML</summary>

```plantum
@startuml "Biểu đồ trình tự Đặt giá"
!theme plain
autonumber "<b>[0]"

actor "Người mua" as buyer
participant "Giao diện" as ui
participant "Hệ thống" as system
database "CSDL" as db

buyer -> ui: Nhập mức giá & nhấn "Đặt giá"
activate ui
ui -> system: Gửi yêu cầu đặt giá 

activate system
system -> db: Lấy giá cao nhất hiện tại & bước giá
activate db
db --> system: Trả về thông tin giá
deactivate db

system -> system: Kiểm tra tính hợp lệ của mức giá
alt Mức giá hợp lệ
    system -> db: Lưu thông tin lượt đặt giá mới
    activate db
    db --> system: Xác nhận lưu thành công
    deactivate db
    system --> ui: Cập nhật real-time cho mọi người trong phiên
else Mức giá không hợp lệ
    system --> ui: Trả về lỗi 
end

ui --> buyer: Cập nhật giao diện
deactivate system
deactivate ui
@enduml
```
</details>

<img width="993" height="533" alt="image" src="https://github.com/user-attachments/assets/893b04cf-630f-481f-b3b4-94b0c1c607c8" />

## Luồng xử lý Tạo Yêu cầu ký gửi
<details>
<summary> Code PlantUML</summary>

```plantum
@startuml "Biểu đồ trình tự Ký gửi Sản phẩm"
!theme plain
autonumber "<b>[0]"

actor "Người bán" as seller
participant "Giao diện" as ui
participant "Hệ thống" as system
database "CSDL" as db

seller -> ui: 1. Truy cập form Ký gửi
activate ui

seller -> ui: 2. Điền thông tin sản phẩm\n
seller -> ui: 3. Nhấn "Gửi yêu cầu"
ui -> system: 4. Gửi thông tin sản phẩm

activate system
system -> system: 5. Kiểm tra tính hợp lệ của dữ liệu
alt Dữ liệu hợp lệ
    system -> db: 6. Lưu thông tin sản phẩm\n
    activate db
    db --> system: 7. Xác nhận lưu thành công
    deactivate db

    system --> ui: 8a. Trả về thông báo thành công
    ui --> seller: 9a. Hiển thị "Gửi yêu cầu thành công"\nvà chuyển trang
else Dữ liệu không hợp lệ
    system --> ui: 8b. Trả về lỗi
    ui --> seller: 9b. Hiển thị thông báo lỗi chi tiết
end
deactivate system
deactivate ui

@enduml
```
</details>

<img width="981" height="607" alt="image" src="https://github.com/user-attachments/assets/4171e246-c696-4732-8dca-edad8f0d1632" />

# Luồng dữ liệu

<details>
<summary> Code PlantUML</summary>

```plantum
@startuml "DFD Cấp 1 - Hệ thống Đấu giá Trang sức"

!define PROCESS circle
!define EXTERNAL_ENTITY rectangle
!define DATA_STORE database

' --- Tác nhân ngoài (External entities) ---
EXTERNAL_ENTITY "Khách hàng (Mua/Bán)" as customer
EXTERNAL_ENTITY "Nhân viên Hệ thống" as staff

' --- Các tiến trình chính (Main processes) ---
PROCESS "1.0\nQuản lý\nTài khoản" as p1_acc_mgmt
PROCESS "2.0\nQuản lý\nSản phẩm" as p2_prod_mgmt
PROCESS "3.0\nQuản lý\nPhiên đấu giá" as p3_sess_mgmt
PROCESS "4.0\nXử lý Đặt giá\n& Giao dịch" as p4_trans_mgmt
PROCESS "5.0\nQuản lý\nBáo cáo" as p5_report_mgmt

' --- Kho dữ liệu (Data stores) ---
DATA_STORE "D1: Dữ liệu Người dùng" as d1_users
DATA_STORE "D2: Dữ liệu Sản phẩm" as d2_products
DATA_STORE "D3: Dữ liệu Phiên & Đặt giá" as d3_auctions
DATA_STORE "D4: Dữ liệu Giao dịch" as d4_transactions

' --- Luồng dữ liệu của Khách hàng ---
customer --> p1_acc_mgmt : Thông tin Đăng ký/Cập nhật
customer --> p2_prod_mgmt : Yêu cầu Ký gửi
p2_prod_mgmt --> customer : Thông báo Trạng thái
p3_sess_mgmt --> customer : Thông tin Phiên đấu giá
customer --> p4_trans_mgmt : Thông tin Đặt giá/Thanh toán
p4_trans_mgmt --> customer : Thông báo Thắng cuộc

' --- Luồng dữ liệu của Nhân viên Hệ thống ---
staff --> p2_prod_mgmt : Thông tin Thẩm định
staff --> p3_sess_mgmt : Yêu cầu Vận hành phiên
staff --> p5_report_mgmt : Yêu cầu xem Báo cáo
p5_report_mgmt --> staff : Dữ liệu Báo cáo

' --- Luộng dữ liệu kết nối Kho dữ liệu ---
p1_acc_mgmt <--> d1_users : Đọc/Ghi dữ liệu người dùng
p2_prod_mgmt <--> d2_products : Đọc/Ghi dữ liệu sản phẩm
p3_sess_mgmt <--> d3_auctions : Đọc/Ghi dữ liệu phiên
p3_sess_mgmt --> d2_products : Đọc dữ liệu sản phẩm
p4_trans_mgmt <--> d3_auctions : Đọc/Ghi dữ liệu đặt giá
p4_trans_mgmt <--> d4_transactions : Đọc/Ghi dữ liệu giao dịch
p5_report_mgmt --> d4_transactions : Đọc dữ liệu giao dịch

@enduml
```
</details>

<img width="1268" height="664" alt="image" src="https://github.com/user-attachments/assets/19bd0e65-f107-4fe4-be5c-b5082c75242e" />

# Các trạng thái thực thể trong hệ thống
## Trạng thái Sản phẩm


<details>
<summary> Code PlantUML</summary>

```plantum
@startuml "Biểu đồ trạng thái Sản phẩm"
!theme plain

[*] --> PendingApproval : Người bán gửi ký gửi
PendingApproval --> Approved : Giám đốc phê duyệt
PendingApproval --> Rejected : Giám đốc từ chối
PendingApproval --> Cancelled : Người bán hủy
Approved --> OnAuction : Nhân viên thêm vào phiên
Approved --> Cancelled : Người bán hủy
OnAuction --> Sold_PendingPayment : Có người thắng cuộc
OnAuction --> Unsold : Hết phiên không có người mua
Sold_PendingPayment --> Sold_PendingDelivery : Người mua thanh toán
Sold_PendingPayment --> Unsold : Hết hạn thanh toán
Sold_PendingDelivery --> Completed : Nhân viên xác nhận bàn giao
Unsold --> Approved: Lên lịch đấu giá lại

state PendingApproval as "Chờ duyệt"
state Approved as "Sẵn sàng đấu giá"
state OnAuction as "Đang đấu giá"
state Sold_PendingPayment as "Chờ thanh toán"
state Sold_PendingDelivery as "Chờ bàn giao"
state Completed as "Đã hoàn tất"
state Unsold as "Không bán được"
state Rejected as "Bị từ chối"
state Cancelled as "Đã hủy"

note right of PendingApproval : Chờ Nhân viên & Giám đốc\nxem xét, thẩm định
note right of Approved : Sản phẩm đã hợp lệ,\nchờ được thêm vào phiên

Rejected --> [*]
Cancelled --> [*]
Completed --> [*]
@enduml
```
</details>

<img width="693" height="764" alt="image" src="https://github.com/user-attachments/assets/818adde7-2e8b-4387-bc7b-d97b6e970a62" />

## Trạng thái Giao dịch  
<details>
<summary> Code PlantUML</summary>

```plantum
@startuml "Biểu đồ trạng thái Giao dịch"
!theme plain

[*] --> PendingPayment : Người mua thắng đấu giá
PendingPayment --> Paid : Người mua thanh toán thành công
PendingPayment --> Failed : Hết hạn thanh toán
PendingPayment --> Cancelled : Quản lý hủy giao dịch
Paid --> Completed : Nhân viên xác nhận bàn giao

state PendingPayment as "Chờ thanh toán"
state Paid as "Đã thanh toán"
state Completed as "Đã hoàn tất"
state Failed as "Thất bại"
state Cancelled as "Đã hủy"

note right of PendingPayment: Giao dịch được tạo,\nchờ người mua thanh toán.
note right of Paid: Người mua đã trả tiền,\nchờ bàn giao sản phẩm.

Completed --> [*]
Failed --> [*]
Cancelled --> [*]
@enduml
```
</details>

<img width="617" height="449" alt="image" src="https://github.com/user-attachments/assets/ba4764eb-7232-4c56-91d8-21a3fe1b5ace" />


# III. Yêu cầu phi chức năng
## Hiệu suất
* Tải trang: Thời gian tải các trang chính không quá 3 giây.

* API phản hồi: Thời gian phản hồi cho các API quan trọngkhông quá 1 giây.

* Chịu tải đồng thời: Hệ thống phải hỗ trợ ổn định ở mức tối thiểu 50 người dùng đặt giá trong một phiên bản đấu giá.

* Tài nguyên tối ưu: Hình ảnh sản phẩm và tài nguyên tĩnh phải được nén và tối ưu hóa để giảm thời gian tải.

## Bảo mật
* Mã hóa dữ liệu: Mật khẩu người dùng và các thông tin nhạy cảm phải được mã hóa mạnh trong cơ sở dữ liệu.

* Chống tấn công: Hệ thống phải có cơ chế phòng chống các loại tấn công web phổ biến, đặc biệt là SQL Injection và Cross-Site Scripting.

* Logging: Ghi lại (log) đầy đủ các hoạt động quan trọng như đăng nhập, thay đổi thông tin, đặt giá, và giao dịch.

* Sao lưu định kỳ: Dữ liệu hệ thống phải được sao lưu tự động theo định kỳ.

## KHả năng mở rộng
* Kiến trúc Module: Hệ thống được xây dựng theo kiến trúc module để dễ dàng bảo trì và thêm tính năng mới.

* Tích hợp bên thứ ba: Kiến trúc phải sẵn sàng cho việc tích hợp với các hệ thống bên thứ ba như cổng thanh toán, dịch vụ vận chuyển.

* Tài liệu hóa: Cung cấp tài liệu API đầy đủ cho các nhà phát triển.

## Giao diện người dùng
* Thiết kế đáp ứng (Responsive): Giao diện phải tương thích và hiển thị tốt trên mọi kích thước màn hình, từ máy tính để bàn đến điện thoại di động.

* Dễ sử dụng: Người dùng mới có thể học và sử dụng các chức năng chính (tìm kiếm, đặt giá) trong vòng dưới 30 phút.

* Tính nhất quán: Giao diện và luồng hoạt động phải nhất quán trên toàn bộ hệ thống.

## Tương thích
 * Trình duyệt: Hoạt động tốt trên các trình duyệt phổ biến: Chrome, Firefox, Safari, Edge.

 * Thiết bị di động: Tương thích với các thiết bị di động chạy hệ điều hành iOS và Android.

 * Tối ưu kết nối: Giao diện và chức năng được tối ưu để hoạt động mượt mà ngay cả trên kết nối mạng chậm.

## ĐỘ tin cậy
* Uptime: Thời gian hoạt động của hệ thống phải đạt tối thiểu 99.9%.

* Phục hồi sau sự cố: Thời gian để phục hồi hệ thống sau khi xảy ra sự cố không quá 4 giờ.

* Kế hoạch dự phòng: Có phương án dự phòng cho cơ sở dữ liệu và máy chủ để đảm bảo an toàn dữ liệu.

## Khả năng bảo trì
* Clean Code: Mã nguồn được viết theo các tiêu chuẩn clean code, dễ đọc và dễ hiểu.

* Tài liệu kỹ thuật: Các chức năng phức tạp và các quyết định kiến trúc quan trọng phải được ghi lại trong tài liệu kỹ thuật.



 # IV. Công nghệ
 # V. Yêu cầu thiết kế
 

* Khả năng Rollback: Quy trình triển khai phải cho phép dễ dàng quay lại phiên bản ổn định trước đó khi phiên bản mới phát sinh lỗi nghiêm trọng.
