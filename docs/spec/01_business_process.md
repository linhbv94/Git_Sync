# Business Process Specification: Git Multi-Sync Tool (`_spec1_business_process`)

> **Version:** 1.0.0  
> **Last Updated:** 2026-08-10  
> **Target Audience:** BA, Dev Agent, System Architect, Operations  

---

## 1. Biểu đồ Quy trình Nghiệp vụ Swimlane (Macro Workflow)

Biểu đồ mô tả sự tương tác vĩ mô ở chế độ dòng lệnh (CLI) giữa **Người dùng (User)**, **Git Sync Engine**, và **Git Remote Repositories**.

```mermaid
graph TB
    subgraph User_Lane [Người Dùng]
        U1[Khởi động CLI Tool] --> U2[Xem Dashboard Trạng thái các Repo]
        U2 --> U3{Chọn hành động trong Menu}
        U3 -- Chọn 1: Smart Sync All --> U4[Hệ thống tự động xử lý]
        U3 -- Chọn 5: Sửa cấu hình --> U5[Thay đổi cấu hình]
        U3 -- Chọn 6: Mở thư mục cấu hình --> U5_OPEN[Yêu cầu mở thư mục cấu hình]
        U3 -- Chọn 7: Thoát --> U6[Kết thúc chương trình]
    end

    subgraph App_Engine_Lane [Git Sync Engine]
        U1 --> E0_CHECK{config.json tồn tại?}
        E0_CHECK -- Chưa có ➔ Chạy Onboarding CLI --> E0_ONBOARD[1. Chọn Lang ➔ 2. Nhập Scan Path ➔ 3. Thêm Ignore (Vòng lặp)]
        E0_ONBOARD --> E0_SAVE[Ghi config.json vào hệ thống]
        E0_SAVE --> E1
        E0_CHECK -- Đã có --> E1[Đọc cấu hình config.json từ AppData/App Support]
        E1 --> E2[Khởi chạy quét đệ quy từ scan_path]
        E2 --> E3{Dưới max_depth, có .git và không bị ignore?}
        E3 -- Đúng ➔ Repo tìm thấy --> E4[Ghi nhận Git Repo & Dừng đệ quy nhánh này]
        E3 -- Sai ➔ Quét tiếp --> E2_RECURSE[Quét các thư mục con]
        E2_RECURSE --> E2
        E4 --> E5[Khởi động Fetch song song: asyncio.gather]
        
        %% GIT OPERATIONS
        E5 --> E6[Kiểm tra status --porcelain và fetch origin]
        E6 --> E7[Phân tích trạng thái chi tiết của từng Repo]
        E7 --> U2
        
        %% EXECUTION
        U4 --> E8{Duyệt qua từng Repo để chạy Smart Sync}
        E8 --> E9{Kiểm tra Repo: Có CLEAN và BEHIND?}
        E9 -- Đúng --> E10[Chạy git pull --ff-only]
        E9 -- Sai --> E11{Kiểm tra Repo: Có CLEAN và AHEAD?}
        E11 -- Đúng --> E12[Chạy git push origin <current_branch>]
        E11 -- Sai --> E13[Bỏ qua an toàn Safe-Skip & Ghi nhận log cảnh báo]
        
        E10 --> E14[Ghi nhận kết quả Sync]
        E12 --> E14
        E13 --> E14
        E14 --> E15[In kết quả báo cáo tổng kết ra Terminal]
        E15 --> U2
        
        %% CONFIG EDITING
        U5 --> E16[Ghi cấu hình mới vào config.json hệ thống]
        E16 --> E2
        
        %% OPEN CONFIG FOLDER
        U5_OPEN --> E17[Chạy lệnh mở thư mục hệ thống: open/explorer]
        E17 --> U2
    end

    subgraph Git_Remote_Lane [Git Remote Repos]
        E6 <--> R1[Fetch commits mới từ Remote]
        E10 <-- R2[Pull commits về Local]
        E12 --> R3[Push commits lên Remote]
    end
```

---

## 2. Ma trận Quyết định (Decision Matrix / Decision Table)

Để đảm bảo tính an toàn tuyệt đối cho mã nguồn cục bộ của người dùng, Sync Engine phải đối chiếu nghiêm ngặt giữa **Trạng thái Working Tree** (Clean/Dirty) và **Trạng thái So sánh Nhánh** (Up-to-date, Ahead, Behind, Diverged, No Remote) để đưa ra hành động tương ứng:

| Trạng thái Working Tree | Trạng thái So sánh Nhánh | Trạng thái Kết nối Mạng | Hành động Đề xuất (CLI Dashboard) | Hành động Thực tế khi chạy Smart Sync | Safe Skip? (Chặn tự động) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **CLEAN** (Sạch) | **UP_TO_DATE** | Online / Offline | Không có thay đổi (Up-to-date) | Bỏ qua (Không cần làm gì) | - |
| **CLEAN** (Sạch) | **BEHIND** | Online | Bị tụt hậu (Behind) -> Đề xuất Pull | Tự động chạy `git pull --ff-only` | **No** (Chạy tự động) |
| **CLEAN** (Sạch) | **AHEAD** | Online | Chạy trước (Ahead) -> Đề xuất Push | Tự động chạy `git push origin <branch>` | **No** (Chạy tự động) |
| **CLEAN** (Sạch) | **DIVERGED** | Online | Lệch nhánh (Diverged) -> Cần Merge tay | **Safe-Skip:** Bỏ qua & Cảnh báo đỏ | **Yes** (Bắt buộc) |
| **CLEAN** (Sạch) | **NO_REMOTE** | Online / Offline | Chưa cấu hình Remote Upstream | Bỏ qua & Hiển thị thông báo màu xám | **Yes** (Bắt buộc) |
| **CLEAN** (Sạch) | **OFFLINE_ERROR**| Offline | Lỗi kết nối mạng khi Fetch | Bỏ qua & Hiển thị cảnh báo vàng | **Yes** (Bắt buộc) |
| **DIRTY** (Chưa commit) | **UP_TO_DATE** | Online / Offline | Có file sửa đổi chưa Commit | **Safe-Skip:** Bỏ qua & Cảnh báo đỏ | **Yes** (Bắt buộc) |
| **DIRTY** (Chưa commit) | **BEHIND** | Online | Có file sửa đổi + Behind | **Safe-Skip:** Bỏ qua & Cảnh báo đỏ | **Yes** (Bắt buộc) |
| **DIRTY** (Chưa commit) | **AHEAD** | Online | Có file sửa đổi + Ahead | **Safe-Skip:** Bỏ qua & Cảnh báo đỏ | **Yes** (Bắt buộc) |
| **DIRTY** (Chưa commit) | **DIVERGED** | Online | Có file sửa đổi + Diverged | **Safe-Skip:** Bỏ qua & Cảnh báo đỏ | **Yes** (Bắt buộc) |
| **DIRTY** (Chưa commit) | **NO_REMOTE** | Online / Offline | Có file sửa đổi + No Remote | **Safe-Skip:** Bỏ qua & Cảnh báo đỏ | **Yes** (Bắt buộc) |

---

## 3. Các Quy tắc Nghiệp vụ bổ sung

1. **Quy tắc bỏ qua thư mục hệ thống (Ignore Rules):** Mặc định, Sync Engine luôn bỏ qua các thư mục sau đây mà không cần người dùng khai báo trong `ignore_list`:
   - Thư mục ẩn hệ điều hành: `.git`, `.idea`, `.vscode`, `node_modules`, `venv`, `.venv`, `__pycache__`.
   - Các file rác: `.DS_Store`, `Thumbs.db`.
2. **Quy tắc xử lý Timeout:** Do lệnh `git fetch` phụ thuộc vào tốc độ mạng và quyền truy cập (SSH/HTTPS), timeout tối đa cho mỗi lệnh fetch song song là **10 giây**. Nếu quá thời gian, Repo đó sẽ được đánh dấu trạng thái là `OFFLINE_ERROR` để tránh làm đơ toàn bộ chương trình.
3. **Quy tắc xác định Branch mặc định:** Chương trình phải tự động lấy tên branch hiện tại đang được checkout tại repo con để thực hiện push/pull, không được mặc định cứng là `main` hoặc `master`.
4. **Quy tắc quét đệ quy (Recursive Scan Rules):** Việc quét đệ quy tìm `.git/` sẽ dừng ngay lập tức tại thư mục phát hiện `.git/`, tránh quét lồng sâu hơn vào bên trong các dự án con (như submodule hay file cache git cục bộ). Độ sâu quét tối đa được giới hạn bởi `max_depth` (mặc định là 3).
