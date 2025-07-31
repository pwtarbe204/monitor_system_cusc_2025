# Monitor System CUSC 2025

Hệ thống giám sát tài nguyên hệ thống máy tính được xây dựng bằng Python Flask, phục vụ nhu cầu theo dõi CPU, RAM, Disk và tốc độ mạng.

---

## 🚀 Cách chạy hệ thống

### Yêu cầu:
- Python 3.x
- Docker (nếu dùng bản container)
- pip (Python package manager)
- Git (nếu clone từ repo)

### Sơ đồ triển khai

![](images/9.png)

### Tải hệ thống về
```bash
git clone https://github.com/pwtarbe204/monitor_system_cusc_2025.git
```
### Cấu hình mật khẩu cho Cơ sở dữ liệu
```
cd monitor_system_cusc_2025
cd system
```
Trong thư mục ```system``` có file ```docker-compose.yml```, tại đây hãy đặt mật khẩu cho cơ sở dữ liệu và nhớ nó.
![Cấu hình docker compose](images/2.png)

Build image, tạo và chạy các container:
```
docker compose up --build
```
### Hướng dẫn cấu hình

Bước 1: Truy cập ```localhost:9001```

![Đường dẫn vào hệ thống](images/1.png)

Bước 2: Set up cơ sở dữ liệu

![](images/4.png)

Bước 3: Đăng kí tài khoản

![](images/5.png)

Bước 4: Đăng nhập vào hệ thống

![](images/6.png)

Bước 5:

![](images/7.png)

## 🚀 Cách chạy Agent

Truy cập vào phần setting nhấn vào nút 3 gach và chọn ```Download Agent```:

![](images/8.png)

Giải nén file zip vừa tải ta sẽ được như thế này:

![](images/10.png)

### 🚀 Cấu hình startup cùng máy tính

Bước 1: Vào mục tìm kiếm tìm ```Task scheduler```

![](images/11.png)

Bước 2: Chọn Create task

![](images/12.png)

Bước 3: Đặt tên cho Task và tick chọn ```Run with highest privileges```

![](images/13.png)

Bước 4: Tạo 2 triggers ```At log on``` với ```At startup```

![](images/14.png)

![](images/15.png)

![](images/16.png)

Bước 5: Tạo action

![](images/17.png)

Đưa đường dẫn đến file .bat của thư mục agent vừa tải

![](images/18.png)

Bước 6: Nhấn Ok và thoát ra, giờ thì File sẽ chạy cùng với máy tính khi bật máy lên.