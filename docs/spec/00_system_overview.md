# System Specification Overview: Git Multi-Sync Tool (`_spec0_system`)

> **Version:** 1.0.0  
> **Last Updated:** 2026-08-10  
> **Target Audience:** Lead Developer, Dev Agents, Test Agents, Product Owner  

---

## 1. Tổng quan Sản phẩm (Product Overview)

**Git Multi-Sync Tool (git_sync)** là công cụ dòng lệnh (CLI) siêu nhẹ chạy đa nền tảng, được thiết kế để tự động quét, kiểm tra trạng thái và đồng bộ hàng loạt các Git repositories nằm trong cùng một thư mục làm việc lớn (Workspace). Thay vì phải truy cập thủ công vào từng thư mục dự án và thực hiện các lệnh git lặp đi lặp lại, công cụ này giúp lập trình viên giám sát toàn bộ dự án cục bộ chỉ với một câu lệnh đơn giản.

### Các nguyên tắc cốt lõi:
1. **Quét đệ quy thông minh (Recursive Scanning):** Tự động phát hiện các Git repositories bằng cách duyệt đệ quy từ thư mục cấu hình (`scan_path`) xuống tối đa `max_depth` (mặc định 3 cấp). Khi phát hiện `.git/` ở bất kỳ thư mục con nào, nhận diện làm Git repo và dừng quét đệ quy sâu hơn tại nhánh đó.
2. **Kiểm tra trạng thái song song (Concurrent Inspecting):** Sử dụng lập trình bất đồng bộ (`asyncio`) để chạy lệnh `git fetch` đồng thời trên tất cả các repositories con được phát hiện, giới hạn concurrency qua `max_concurrency`.
3. **Phân loại trạng thái an toàn (Strict Status Classification):** Nhận diện chính xác 6 trạng thái Git cục bộ và từ xa: `UP_TO_DATE`, `BEHIND`, `AHEAD`, `DIVERGED`, `DIRTY`, và `NO_REMOTE`.
4. **Mặc định an toàn (Safe by Default):** Chỉ tự động đồng bộ (Smart Sync) đối với các repository có trạng thái sạch (`CLEAN` working tree). Bất kỳ thay đổi chưa commit nào (`DIRTY`) hoặc phân nhánh lệch (`DIVERGED`) sẽ bị chặn đồng bộ tự động để bảo toàn mã nguồn gốc.

---

## 2. Bản đồ Hồ sơ Đặc tả (Specification Index)

Tất cả các tài liệu đặc tả liên kết bằng đường dẫn tương đối:

- 📋 [01_business_process.md](01_business_process.md): Sơ đồ Swimlane vĩ mô & Ma trận Quyết định Smart Sync (`_spec1_business_process`)
- 🔄 [02_feature_flow.md](02_feature_flow.md): Luồng Logic, User Flow, State Machine & Resolution Flow (`_spec2_feature_flow`)
- 🎨 [03_ui_wireframe.md](03_ui_wireframe.md): Giao diện Dòng lệnh CLI Terminal & Dashboard màu sắc (`_spec3_ui_wireframe`)
- 🗄️ [04_api_data.md](04_api_data.md): Schema config.json & cấu trúc dữ liệu (`_spec4_api_data`)
- 🧪 [05_qa_acceptance.md](05_qa_acceptance.md): Tiêu chí Nghiệm thu Gherkin & Ma trận Edge Cases (`_spec5_qa_acceptance`)
- 🎬 [06_demo_presentation.md](06_demo_presentation.md): Kịch bản Trình diễn Demo CLI (`_spec6_demo_presentation`)

---

## 3. Kiến trúc Tổng thể Hệ thống (System Architecture)

```text
 ┌─────────────────────────────────────────────────────────────────────────┐
 │ Workspace Thư mục cha (Cấu hình quét hoặc Thư mục hiện tại)             │
 │                                                                         │
 │  ┌───────────────────────┐                                              │
 │  │ CLI Git Sync Tool     │◄────────────────────────────────┐            │
 │  │   [sync_engine]       │ (Đọc cấu hình hệ thống)         │            │
 │  └──────────┬────────────┘                                 │            │
 │             │ (Recursive Scan & Async Fetch)               │            │
 │             ▼                                              │            │
 │   ┌─────────┼───────────┬───────────────┬──────────────────│────────────┐   │
 │   │         │           │               │                  │            │   │
 │   ▼         ▼           ▼               ▼                  │            ▼   │
 │ ┌───┐     ┌───┐       ┌───┐           ┌───┐                │          ┌───┐ │
 │ │r1 │     │r2 │       │r3 │           │r4 │                │          │rn │ │
 │ │.git     │.git       │.git           │.git                │          │.git │
 │ └───┘     └───┘       └───┘           └───┘                │          └───┘ │
 └─────────────┬───────────┬───────────────┬──────────────────│────────────┘
               │           │               │ (git fetch/pull/push)│
               ▼           ▼               ▼                  │
 ┌────────────────────────────────────────────────────────────│────────────┐
 │ Git Remote (GitHub / GitLab / Bitbucket)                   │            │
 │ ┌───────────┐ ┌──────────┐ ┌───────────┐ ┌───────────┐     │   ┌──────┐ │
 │ │remote_r1  │ │remote_r2│ │remote_r3  │ │remote_r4  │     │   │rem_rn│ │
 │ └───────────┘ └──────────┘ └───────────┘ └───────────┘     │   └──────┘ │
 └────────────────────────────────────────────────────────────│────────────┘
                                                              │
 ┌────────────────────────────────────────────────────────────│────────────┐
 │ AppData / Application Support                              │            │
 │ ┌──────────────────────────────────────────────────────────┴──────────┐ │
 │ │ file: config.json (scan_path, ignore_list, max_depth, timeout)      │ │
 │ └─────────────────────────────────────────────────────────────────────┘ │
 └─────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Định dạng File Thực thi & Cơ chế Phím tắt (Shortcuts)

| Hệ điều hành | Định dạng File | Cơ chế Phím tắt 1-Click |
| :--- | :--- | :--- |
| **Windows** | `.exe` (PE Binary) | Tạo shortcut trỏ đến tệp thực thi `.exe`, ghim tại Desktop/Taskbar. File cấu hình được nạp tự động từ thư mục AppData hệ thống. |
| **macOS** | **Unix Executable** | Sử dụng file `.command` hoặc script Automator để cd vào thư mục chứa tệp nhị phân và chạy ngay lập tức bằng cách click đúp. |

---

## 5. Ranh giới Nghiệp vụ & Phạm vi (Scope Matrix)

| Tính năng | Trong Phạm vi (In-Scope) | Ngoài Phạm vi (Out-of-Scope) |
| :--- | :--- | :--- |
| **Giao diện** | Giao diện dòng lệnh CLI (sử dụng màu ANSI cho bảng trạng thái), chế độ interactive. | Giao diện đồ họa phức tạp (GUI App). |
| **Cơ chế Sync** | Quét đệ quy tìm Git repos (độ sâu tối đa config), `git fetch origin` ngầm song song, tự động `git pull --ff-only` cho BEHIND, `git push` cho AHEAD. | Tự động giải quyết merge conflict, tự động `git add .` và commit bừa bãi. |
| **An toàn** | Luôn chạy `git status --porcelain` trước khi sync. Chặn tuyệt đối mọi can thiệp nếu working tree bị `DIRTY`. | Thực hiện `git reset --hard` hoặc `git push --force` gây mất code người dùng khi chưa được chỉ thị rõ. |
| **Cấu hình** | Cấu hình lưu trữ tại AppData/Application Support; Cho phép thay đổi `scan_path`, `ignore_list`, `max_depth`, `timeout` qua config. | Quản lý hoặc lưu trữ credentials của người dùng (dùng SSH/Keychain mặc định của OS). |

---

## 6. Tiêu chuẩn Thực thi cho AI Execution Agents (Ground Truth)

Khi AI Dev Agent thực hiện viết mã dự án này, bắt buộc tuân thủ:
1. **Ngôn ngữ:** Python 3.10+ (Không sử dụng thư viện bên ngoài để thực hiện lệnh Git như GitPython, thay vào đó chạy trực tiếp subprocess của Git CLI hệ thống).
2. **Chia sẻ Thư viện:** Thừa kế hoặc mở rộng mã nguồn lớp `GitEngine` từ dự án [git_engine.py](../skills_sync/src/git_engine.py) trong `skills_sync` để tái sử dụng tối đa logic phân tích trạng thái.
3. **Bất đồng bộ:** Sử dụng `asyncio` để khởi tạo các luồng chạy subprocess song song khi fetch dữ liệu của nhiều repo cùng lúc.
4. **Mã lỗi & Trả về:** Trả về rõ ràng các exception và ghi nhận log chi tiết thời gian chạy quét.
