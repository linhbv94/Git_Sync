# Demo & Presentation Specification: Git Multi-Sync Tool (`_spec6_demo_presentation`)

> **Version:** 1.0.0  
> **Last Updated:** 2026-08-10  
> **Target Audience:** Product Owner, Client, Dev Team, QA Team  

---

## 1. Hướng dẫn thiết lập môi trường Demo (Setup Playbook)

Để trình diễn được đầy đủ tính năng phân tích và đồng bộ an toàn của **Git Multi-Sync Tool**, cần thiết lập một thư mục demo chứa các repositories mô phỏng 5 trạng thái cốt lõi ở nhiều cấp thư mục:

1.  **Repo 1 (`up_to_date_repo`):** Sạch (clean working tree), đồng bộ hoàn toàn với remote.
2.  **Repo 2 (`ahead_repo`):** Sạch, tạo thêm 1-2 commits cục bộ chưa push lên remote.
3.  **Repo 3 (`tools/dirty_tool`):** Nằm trong thư mục con `tools/`, có thay đổi chưa commit (sửa đổi file bất kỳ).
4.  **Repo 4 (`web_app`):** Sạch, giả lập remote có commit mới, local chưa pull về.
5.  **Repo 5 (`tools/diverged_tool`):** Nằm trong thư mục con `tools/`, cả cục bộ và remote đều có commit mới khác nhau.

---

## 2. Kịch bản Trình diễn Từng bước (Step-by-Step CLI Presentation)

### Bước 0: Trình diễn Quy trình Onboarding ban đầu (Initial Onboarding Setup)
*   **Hành động:** Xóa file `config.json` trong thư mục AppData/Application Support hệ thống (nếu có), sau đó chạy lệnh `python main.py` để khởi động tool ở chế độ trắng.
*   **Điểm cần nhấn mạnh (Talking Points):**
    *   *“Khi khởi chạy lần đầu tiên, hệ thống phát hiện chưa có file cấu hình và sẽ tự động bắt đầu quy trình thiết lập tương tác Onboarding.”*
    *   *“Người dùng chọn phím bấm `2` để thiết lập hiển thị bằng Tiếng Việt.”*
    *   *“Tiếp theo, ta thiết lập scan_path. Tôi chỉ cần nhấn Enter để mặc định lấy thư mục hiện tại.”*
    *   *“Quy trình cấu hình Ignore List rất tiện lợi: ta nhập hoặc paste thư mục cần ignore ➔ Nhấn Enter để thêm ➔ Hệ thống lập tức hiển thị list cập nhật và cho phép nhập tiếp. Khi đã xong, ta chỉ cần nhấn Enter trực tiếp trên dòng trống để hoàn tất cấu hình và chuyển thẳng vào Dashboard chính.”*

### Bước 1: Khởi động & Quét Trạng thái Ban đầu (Scan Initialization)
*   **Hành động:** Chạy lệnh `python main.py` trong thư mục cha chứa các dự án mô phỏng trên.
*   **Điểm cần nhấn mạnh (Talking Points):**
    *   *“Tool tự động tìm thấy cấu hình `config.json` hệ thống (lưu tại AppData/Application Support) và khởi chạy quét đệ quy với `max_depth = 3`.”*
    *   *“Nhờ cơ chế quét đệ quy thông minh, tool dễ dàng tìm thấy các dự án nằm ở thư mục con cấp 2 như `tools/dirty_tool` và `tools/diverged_tool`.”*
    *   *“Quá trình quét và git fetch origin song song cho tất cả các repo chỉ mất chưa đầy 3 giây nhờ cơ chế asyncio.”*

### Bước 2: Thuyết minh Dashboard Trạng thái (Dashboard Explanation)
*   **Hành động:** Chỉ vào bảng kết quả in ra Terminal.
*   **Điểm cần nhấn mạnh:**
    *   **Màu xanh lá:** Giải thích `up_to_date_repo` đang đồng bộ hoàn hảo.
    *   **Màu vàng (Behind/Ahead):** Chỉ rõ `web_app` bị chậm commits (▼1) và `ahead_repo` đang chạy trước 2 commits (▲2). Hệ thống đề xuất tự động pull và push.
    *   **Cảnh báo đỏ (Dirty/Diverged):** Giải thích lý do `tools/dirty_tool` và `tools/diverged_tool` hiển thị cảnh báo nguy hiểm. Tool tự đề xuất bỏ qua tự động (Safe-Skip) để bảo toàn code đang viết dở của lập trình viên.

### Bước 3: Thực thi Smart Sync (Executing Auto Sync)
*   **Hành động:** Nhập phím `1` và nhấn Enter để kích hoạt chế độ **Smart Sync All**.
*   **Điểm cần nhấn mạnh:**
    *   *“Tool sẽ tuần tự đồng bộ các repo an toàn. Mời anh/chị xem log chạy thực tế.”*
    *   *“`ahead_repo` được push thành công. `web_app` được pull fast-forward thành công.”*
    *   *“Các repo `tools/dirty_tool` và `tools/diverged_tool` được phát hiện có rủi ro nên hệ thống hiển thị thông báo Safe Skip màu vàng và bỏ qua hoàn toàn, không đè hay làm mất code cục bộ.”*

### Bước 4: Kiểm tra kết quả sau Sync (Verification)
*   **Hành động:** Nhấn Enter để quay lại Dashboard.
*   **Điểm cần nhấn mạnh:**
    *   *“Bây giờ, trên Dashboard, cả `ahead_repo` và `web_app` đều đã chuyển sang trạng thái CLEAN và UP_TO_DATE (Màu xanh lá).”*
    *   *“Chỉ còn lại các repo trong thư mục `tools/` bị dirty và diverged cần người dùng tự xử lý tay là vẫn giữ nguyên cảnh báo đỏ ban đầu.”*

### Bước 5: Chỉnh sửa cấu hình quét (Configuration Customization)
*   **Hành động:** Chọn phím `5` (Edit Config), chọn `1` (Sửa scan_path) và nhập đường dẫn mới.
*   **Điểm cần nhấn mạnh:**
    *   *“Tool cho phép người dùng thay đổi thư mục quét, danh sách ignore và cả độ sâu quét max_depth trực quan ngay trên menu CLI mà không cần mở file json cấu hình.”*
