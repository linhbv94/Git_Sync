# GIT MULTI-SYNC TOOL (v1.0.0) - MASTER PRODUCT REQUIREMENT DOCUMENT (PRD)

---

## DOCUMENT CONTROL

*   **Google Doc ID:** `xxx`
*   **Tab ID:** `xxx`

### 1. Project Stakeholders (RACI)
*   **Product Owner / PM:** User (vic) - Người đưa ra yêu cầu sản phẩm và phê duyệt tính năng.
*   **Tech Lead / Dev:** Antigravity AI Agent - Người thiết kế kiến trúc kỹ thuật và lập trình.
*   **QA/QC:** Antigravity AI Agent & User - Kiểm thử chất lượng và sự ổn định.

### 2. Glossary & Terminology (Thuật ngữ)
*   **Workspace (Thư mục cha):** Thư mục chứa tất cả các thư mục dự án nhỏ bên trong và chứa cả thư mục chạy tool.
*   **DIRTY (Thư mục bẩn):** Repo chứa các tệp tin có thay đổi chưa được commit (staged hoặc unstaged changes, untracked files).
*   **AHEAD (Chạy trước):** Nhánh local hiện tại có commit mới hơn remote upstream branch nhưng chưa được `push`.
*   **BEHIND (Bị tụt hậu):** Nhánh remote upstream branch có commit mới hơn local branch nhưng chưa được `pull`.
*   **DIVERGED (Phân nhánh lệch):** Cả local và remote đều có các commit mới khác nhau, đòi hỏi phải merge hoặc rebase để đồng bộ.
*   **UP_TO_DATE (Đồng bộ):** Local branch trùng khớp hoàn toàn với remote upstream branch.
*   **NO_REMOTE:** Repo Git local chưa được liên kết hoặc chưa thiết lập tracking upstream branch (`origin/<branch>`).

### 3. Key Resources & References (Liên kết tài nguyên)
*   **Workspace Link:** [git_sync_prd.md](git_sync_prd.md)
*   **Tham chiếu logic:** [git_engine.py](../skills_sync/src/git_engine.py)

---

## I. Overview (Executive Summary)

### 1. Document Goal
Tài liệu PRD này định nghĩa các yêu cầu nghiệp vụ, tính năng kỹ thuật và trải nghiệm người dùng đối với ứng dụng **Git Multi-Sync Tool (git_sync)**. Đây là một công cụ dòng lệnh (CLI) độc lập, giúp các lập trình viên quản lý nhiều Git Repositories trong cùng một thư mục làm việc lớn mà không cần phải truy cập thủ công vào từng dự án để kiểm tra và đồng bộ.

### 2. Product Scope
*   **In Scope (Phát triển trong phiên bản đầu tiên):**
    *   Tự động quét toàn bộ thư mục con nằm cùng cấp với file thực thi của tool để tìm thư mục `.git`.
    *   Tự động `git fetch` song song hoặc bất đồng bộ để tối ưu hiệu năng tốc độ quét.
    *   Nhận diện 6 trạng thái cốt lõi: `UP_TO_DATE`, `AHEAD`, `BEHIND`, `DIVERGED`, `DIRTY`, và `NO_REMOTE`.
    *   Hiển thị bảng báo cáo trạng thái trực quan trong Terminal (sử dụng màu sắc ANSI).
    *   Chế độ tự động thông minh (Smart Auto Sync):
        *   Tự động chạy `git pull --ff-only` cho các repo ở trạng thái `BEHIND` (khi local đang sạch).
        *   Tự động chạy `git push` cho các repo ở trạng thái `AHEAD` (khi local đang sạch).
    *   Cảnh báo đỏ và bỏ qua một cách an toàn (Safe Skip) đối với các repo ở trạng thái `DIRTY` hoặc `DIVERGED` để tránh xung đột mã nguồn và mất dữ liệu của người dùng.
*   **Out of Scope (Chưa phát triển):**
    *   Giao diện đồ họa (GUI App).
    *   Tự động giải quyết xung đột merge conflict (đòi hỏi người dùng vào xử lý thủ công).
    *   Tự động commit các thay đổi thô mà không có thông báo cụ thể từ người dùng.

---

## II. Vision, Goals & Success Metrics

### 1. Product Vision
*   **North Star (Dài hạn):** Trở thành một CLI tiện ích gọn nhẹ, tin cậy nhất cho các lập trình viên quản lý hàng trăm repositories cục bộ, giúp việc đồng bộ hóa dữ liệu làm việc giữa các máy trạm lên GitHub/GitLab diễn ra trơn tru chỉ với 1 click hoặc thiết lập cron job tự động.

### 2. Product Goals (Ngắn hạn)
*   Tối ưu hóa thời gian kiểm tra mã nguồn hàng ngày. Lập trình viên không cần chạy chuỗi lệnh `git status`, `git pull`, `git push` cho từng repo đơn lẻ.
*   Bảo vệ dữ liệu, tránh tình trạng code viết xong ở máy công ty nhưng quên `push` trước khi về nhà làm việc tiếp trên máy cá nhân.

### 3. Success Metrics & High-level Analytics

| Metric Type | Metric Name | Definition | Cách đo / Tool đo | Target |
| :--- | :--- | :--- | :--- | :--- |
| **Primary** | Quét & Phân tích Tốc độ | Thời gian trung bình để quét và báo cáo trạng thái của 10 dự án | Đo log thời gian chạy script | < 5 giây (khi có mạng ổn định) |
| **Primary** | Tỉ lệ lỗi mất mã nguồn | Số lượng sự cố mất dữ liệu do tool tự động đồng bộ đè | Đo lường phản hồi QA | **0 sự cố** (Độ an toàn tuyệt đối) |
| **Secondary** | Tỉ lệ thành công FF-Pull | Phần trăm các tác vụ pull không gây xung đột được thực hiện tự động | Đo log nội bộ | > 95% các repo BEHIND sạch |

---

## III. Problem, Target Audience & Context

### 1. Target Audience (Chân dung người dùng)
*   **Lập trình viên chuyên nghiệp:** Người làm việc trên nhiều dự án nhỏ cùng một lúc (Microservices, nhiều thư viện code riêng, hoặc lưu trữ ghi chú cá nhân dạng markdown) nằm trong cùng một Workspace mẹ.
*   **Người làm việc Hybrid:** Di chuyển thường xuyên giữa máy công ty và máy cá nhân tại nhà, cần các dự án luôn đồng bộ trạng thái mới nhất lên Git.

### 2. Problem Statement
*   **Tốn thời gian:** Việc đi vào từng thư mục dự án gõ lệnh `git fetch`, `git status`, `git pull`, `git push` rất tẻ nhạt và tốn thời gian khi số lượng dự án tăng từ 5-10 trở lên.
*   **Dễ quên:** Rất dễ quên `push` một số dự án phụ trước khi tắt máy. Khi về nhà mở máy tính cá nhân lên làm việc mới phát hiện code chưa được đẩy lên Remote.
*   **Sợ mất mát/xung đột dữ liệu:** Không dám dùng các script tự động pull/push thô sơ (dạng bash loop gõ bừa lệnh pull/push) vì sợ nó tự ý ghi đè gây mất code đang sửa dở hoặc sinh lỗi merge conflict hỗn độn.

### 3. Current Alternatives
*   **Bash script loop đơn giản:** Viết vòng lặp `for dir in *; do cd $dir && git pull && git push; done`.
    *   *Điểm yếu:* Chạy tuần tự cực kỳ chậm, không fetch trước để kiểm tra, dễ lỗi giữa chừng, tự động push đè hoặc pull lỗi đè lên code chưa commit gây hư hỏng workspace.
*   **Ứng dụng GUI (như SourceTree, GitHub Desktop):**
    *   *Điểm yếu:* Nặng nề, phải import thủ công từng repo một vào app, không có nút "Đồng bộ tất cả các repo bị lệch nhánh chỉ trong 1 click".

---

## IV. Solution & Capabilities

### 1. Value Proposition (Định vị giá trị)
**Git Multi-Sync Tool** là cầu nối an toàn và siêu tốc giúp giám sát và đồng bộ đa repo. Chỉ can thiệp đồng bộ tự động đối với các repo ở trạng thái "Xanh sạch" (Clean) và đưa ra cảnh báo đỏ ngay lập tức đối với những dự án cần người dùng can thiệp để bảo toàn code tối đa.

### 2. Core Capabilities
*   **Auto Scanning (Quét tự động):** Quét trực tiếp danh sách thư mục con tại thư mục hiện tại chứa file thực thi (`./`), tự động nhận dạng các dự án có chứa `.git/` để đưa vào hàng đợi kiểm tra.
*   **Multi-thread / Async Fetching (Kiểm tra song song):** Sử dụng lập trình bất đồng bộ (`asyncio` trong Python hoặc multi-threading) để thực hiện lệnh `git fetch` đồng thời trên toàn bộ các repositories giúp thời gian quét cực kỳ nhanh.
*   **Trạng thái an toàn (Clean check):** Luôn kiểm tra `git status --porcelain` trước khi thực hiện bất kỳ lệnh đồng bộ nào.
*   **Bảng báo cáo trực quan (Beautiful Dashboard):** Hiển thị bảng tổng hợp sắc nét ngay trên terminal gồm: Tên dự án, Branch hiện tại, Trạng thái (Clean/Dirty), Số commit lệch (Ahead/Behind) và Hành động đề xuất.

---

## V. Business & UX Strategy

### 1. UX Philosophy
*   **Terminal-first, Minimalist & Clear:** Bảng hiển thị thông tin phải phân chia màu sắc trực quan (Đỏ cho Dirty/Diverged, Vàng cho Behind/Ahead, Xanh cho Up-to-date).
*   **Safe by Default (Mặc định an toàn):** Không bao giờ tự ý chạy `git push --force` hoặc tự commit tệp tin bị dirty trừ khi người dùng cấp quyền explicitly.

### 2. Activation Moment (Aha-moment)
*   Khi người dùng chạy tool lần đầu tiên, chỉ mất **3 giây** để thấy toàn bộ danh sách 15 dự án của mình được sắp xếp hiển thị trạng thái chuẩn xác kèm theo thông tin chi tiết từng branch hiện hành.

---

## VI. Core Product Flows

### 1. Initial Setup (Onboarding Flow - Run once when config.json does not exist)
1.  **Bước 1: Khởi động lần đầu** ➔ Nếu không tìm thấy file cấu hình `config.json` hệ thống, tool tự động kích hoạt tiến trình Onboarding ban đầu.
2.  **Bước 2: Lựa chọn Ngôn ngữ** ➔ Người dùng nhập số `1` (Tiếng Việt) hoặc `2` (Tiếng Anh).
3.  **Bước 3: Nhập đường dẫn quét** ➔ Người dùng paste/nhập đường dẫn tuyệt đối đến Workspace quét, hoặc nhấn Enter để mặc định lấy thư mục hiện tại.
4.  **Bước 4: Nhập danh sách ignore (Interactive Loop)** ➔ Người dùng nhập hoặc paste lần lượt từng tên thư mục/đường dẫn cần bỏ qua và nhấn Enter để thêm. Khi muốn kết thúc cấu hình, người dùng nhấn Enter trực tiếp trên dòng trống.
5.  **Bước 5: Hoàn tất cấu hình** ➔ Tool tự động tạo thư mục AppData/Application Support và ghi nhận thông tin cấu hình ban đầu vào tệp `config.json`. Sau đó, chuyển tiếp người dùng trực tiếp vào Dashboard Menu chính.

### 2. Core User Journey (Daily Operations)
1.  **Bước 1: Khởi động** ➔ Người dùng kích hoạt file thực thi của tool. Tool tự động nạp cấu hình `config.json` đã lưu từ hệ thống.
2.  **Bước 2: Quét & Phân tích** ➔ Tool tự động chạy thuật toán quét đệ quy từ `scan_path` tối đa `max_depth` (không quét sâu hơn khi gặp `.git` và bỏ qua các thư mục ignore) để lấy danh sách Git repos, đồng thời thực thi lệnh `git fetch` ngầm song song cho từng repo.
3.  **Bước 3: Báo cáo** ➔ Tool in bảng trạng thái chi tiết của tất cả repositories con phát hiện được.
4.  **Bước 4: Thực thi (Smart Sync)** ➔ Người dùng có thể chọn các chức năng từ Menu:
    *   `[1]` Smart Sync All (Pull các repo BEHIND đang sạch, Push các repo AHEAD đang sạch).
    *   `[2]` Chỉ Smart Pull.
    *   `[3]` Chỉ Smart Push.
    *   `[4]` Làm mới trạng thái (Refresh).
    *   `[5]` Sửa đổi cấu hình.
    *   `[6]` Mở thư mục cấu hình.
    *   `[7]` Thoát.
5.  **Bước 5: Hoàn tất** ➔ Tool thực hiện các lệnh Git tương ứng, báo cáo kết quả thành công/thất bại và quay lại Dashboard chính.

---

## VII. Requirements & Architecture

### 1. Functional Requirements (Yêu cầu chức năng)

| ID | Feature Name | Description | Priority |
| :--- | :--- | :--- | :--- |
| **FR-01** | Quét dự án đệ quy tự động | Quét đệ quy từ thư mục cấu hình `scan_path` xuống tối đa `max_depth` (mặc định 3 cấp) để tìm `.git/`. Nhận dạng làm Git repo và dừng quét sâu hơn tại nhánh đó. Hỗ trợ bỏ qua các thư mục trong `ignore_list`. | Must-have |
| **FR-02** | Fetch dữ liệu ngầm | Thực hiện `git fetch origin` ngầm trước khi so sánh phiên bản nhằm lấy thông tin chính xác nhất từ Server. | Must-have |
| **FR-03** | Phân tích trạng thái | Xác định trạng thái của từng repo: `UP_TO_DATE`, `BEHIND`, `AHEAD`, `DIVERGED`, `DIRTY`, `NO_REMOTE`. | Must-have |
| **FR-04** | Hiển thị Dashboard | In ra bảng CLI hiển thị các cột: Dự án | Nhánh | Trạng thái file | Đồng bộ | Hành động đề xuất. | Must-have |
| **FR-05** | Tự động Pull an toàn | Đối với repo `BEHIND` và Trạng thái file là `CLEAN`, chạy `git pull --ff-only`. Nếu thất bại (conflict), chuyển trạng thái repo sang cảnh báo lỗi. | Must-have |
| **FR-06** | Tự động Push an toàn | Đối với repo `AHEAD` và Trạng thái file là `CLEAN`, chạy `git push origin <branch>`. | Must-have |
| **FR-07** | Cấu hình hệ thống tập trung | Đọc và ghi tệp cấu hình `config.json` lưu trữ tại thư mục AppData/Application Support của hệ thống để người dùng chỉnh sửa đường dẫn quét, danh sách bỏ qua, độ sâu quét... | Should-have |
| **FR-08** | Quy trình Onboarding thiết lập ban đầu | Hiển thị CLI hướng dẫn người dùng cấu hình lần đầu (chọn ngôn ngữ, scan_path, ignore_list đệ quy) và tự động lưu file config hệ thống khi hoàn tất. | Must-have |
| **FR-09** | Mở thư mục cấu hình | Cho phép người dùng chọn chức năng mở thư mục lưu trữ cấu hình hệ thống bằng File Explorer/Finder của OS để dễ dàng chỉnh sửa thủ công. | Should-have |

### 2. Non-functional Requirements (Yêu cầu phi chức năng)
*   **Performance:** Sử dụng lập trình bất đồng bộ để quét và fetch nhiều repo đồng thời. Thời gian kiểm tra 10 repo không vượt quá 5 giây trên môi trường mạng thông thường.
*   **Robustness (Tính bền bỉ):**
    *   Không bị đơ/treo terminal khi gặp lỗi xác thực Git Remote (Token hết hạn hoặc sai SSH Key). Tự động bỏ qua repo lỗi Auth và tiếp tục xử lý các repo khác.
    *   Không gây mất mát dữ liệu local của người dùng dưới bất kỳ lỗi ngầm định nào.
*   **Compatibility:** Chạy độc lập tốt trên macOS, Linux và Windows. Không yêu cầu các thư viện cài thêm phức tạp (chỉ dùng Python Standard Library nếu viết bằng Python).

### 3. Technical Architecture Overview
*   **Ngôn ngữ lập trình đề xuất:** Python (phiên bản 3.8+).
*   **Thành phần chính:**
    1.  `config_manager`: Quản lý tệp `config.json` (chứa workspace path, list các thư mục cần ignore).
    2.  `scanner`: Quét các thư mục con, phát hiện Git repositories.
    3.  `git_inspector`: Thực hiện các lệnh Git subprocess (`status`, `fetch`, `rev-list`, `rev-parse`) để phân tích trạng thái từng repo.
    4.  `dashboard`: Định dạng bảng biểu hiển thị ra màn hình terminal với màu sắc trực quan.
    5.  `sync_engine`: Thực thi logic pull, push và xử lý ngoại lệ an toàn.

---

## VIII. Roadmap & Rollout Strategy

### 1. Product Roadmap
*   **Phase 1 (MVP - CLI):** Hoàn thành lõi CLI quét, check status và hiển thị Dashboard. Hỗ trợ tự động Pull/Push cơ bản trên nhánh `main`/`master` cục bộ.
*   **Phase 2 (Đa Nhánh & Cấu hình):** Hỗ trợ nhận diện nhánh bất kỳ đang checkout, cho phép cấu hình `config.json` chi tiết hơn và tối ưu hóa fetch song song.
*   **Phase 3 (Đóng gói & Phân phối):** Đóng gói thành file thực thi độc lập (dạng `.exe` cho Windows và binary chạy trực tiếp trên macOS) sử dụng PyInstaller giúp phân phối dễ dàng không cần cài Python.

---

## IX. Risks, Assumptions & Actions (RAA)

| ID | Type | Description | Impact (H/M/L) | Action / Mitigation Plan |
| :--- | :--- | :--- | :--- | :--- |
| **RAA-01** | Risk | Người dùng cấu hình sai hoặc gặp lỗi mạng giữa chừng khiến lệnh `git pull` bị treo. | Medium | Thiết lập tham số `timeout=10` giây cho mọi lệnh `git subprocess`. Nếu quá thời gian, đánh dấu trạng thái repo là `TIMEOUT` và bỏ qua. |
| **RAA-02** | Risk | Thiết lập tự động pull đè gây mất code đang sửa dở của người dùng. | High | **Quy tắc chặn tuyệt đối:** Tool chỉ pull/push tự động khi kết quả kiểm tra `git status --porcelain` rỗng hoàn toàn (Clean). Nếu có bất kỳ tệp tin nào bị dirty, tool chỉ cảnh báo và không can thiệp. |
| **RAA-03** | Assumption | Tool hoạt động với các máy đã được cài sẵn Git CLI và người dùng đã cấu hình quyền SSH/Keychain SSH thành công trên máy cục bộ. | High | Tool sẽ kiểm tra xem lệnh `git` có khả dụng trong hệ thống hay không khi bắt đầu khởi chạy. Nếu chưa có Git, hiển thị thông tin hướng dẫn tải Git CLI. |

---

## X. Version History

| Version | Date | Author | Description of Changes | Status |
| :--- | :--- | :--- | :--- | :--- |
| v1.0 | 10/08/2026 | Antigravity | Initial Draft - Khởi tạo tài liệu PRD cho Git Multi-Sync Tool | Approved |
