# UI Wireframe Specification: Git Multi-Sync Tool (`_spec3_ui_wireframe`)

> **Version:** 1.0.0  
> **Last Updated:** 2026-08-10  
> **Target Audience:** UI Engineer, Dev Agent, QA/Test Agent  

---

## 0. Quy trình Onboarding thiết lập ban đầu (Initial Setup CLI UI)

Khi ứng dụng chạy lần đầu và không tìm thấy tệp cấu hình `config.json` hệ thống:

### A. Chọn ngôn ngữ hiển thị (Select Language Screen)
```text
======================================================================
⚡ GIT MULTI-SYNC TOOL - CẤU HÌNH BAN ĐẦU / INITIAL SETUP
======================================================================
💡 config.json không tồn tại. Bắt đầu thiết lập ban đầu.
💡 config.json not found. Starting initial configuration.

Vui lòng chọn ngôn ngữ hiển thị / Please select display language:
  [1] English (en)
  [2] Tiếng Việt (vi)

Lựa chọn của bạn / Your choice (1/2): _
```

### B. Thiết lập Thư mục Quét (Scan Path Setup Screen)
*(Giả sử chọn Tiếng Việt ở bước trên)*
```text
======================================================================
⚡ GIT MULTI-SYNC TOOL - CẤU HÌNH BAN ĐẦU (Tiếng Việt)
======================================================================
💡 Vui lòng nhập đường dẫn tuyệt đối đến Thư mục cha (Workspace) cần quét.
(Nhấn Enter trực tiếp để mặc định lấy thư mục hiện tại: /Users/vic/_Work/zTool)

Nhập đường dẫn: _
```

### C. Vòng lặp thêm ignore (Ignore List Interactive Loop Screen)
#### 1. Bước nhập phần tử đầu tiên:
```text
======================================================================
⚡ GIT MULTI-SYNC TOOL - CẤU HÌNH BAN ĐẦU (Tiếng Việt)
======================================================================
💡 Vui lòng nhập tên thư mục hoặc đường dẫn cần bỏ qua khi quét (ignore_list).
(Nhấn Enter trực tiếp trên dòng trống để HOÀN TẤT cấu hình).

[DANH SÁCH BỎ QUA HIỆN TẠI]: ["node_modules", "venv", ".venv", "build", "dist"]

Nhập thư mục cần ignore tiếp theo (nhấn Enter để xong): tools/temp_dir_
```

#### 2. Danh sách được cập nhật và tiếp tục loop:
```text
======================================================================
⚡ GIT MULTI-SYNC TOOL - CẤU HÌNH BAN ĐẦU (Tiếng Việt)
======================================================================
💡 Vui lòng nhập tên thư mục hoặc đường dẫn cần bỏ qua khi quét (ignore_list).
(Nhấn Enter trực tiếp trên dòng trống để HOÀN TẤT cấu hình).

[DANH SÁCH BỎ QUA HIỆN TẠI]: ["node_modules", "venv", ".venv", "build", "dist", "tools/temp_dir"]

Nhập thư mục cần ignore tiếp theo (nhấn Enter để xong): _
```
*(Người dùng nhấn Enter trực tiếp trên dòng trống này ➔ Hệ thống lưu tệp config.json và chuyển vào màn hình Quét).*

---

## 1. Màn hình Khởi động & Quét trạng thái (Scanner Loading CLI)

Khi người dùng khởi chạy lệnh chạy hoặc phím tắt của tool:

```text
======================================================================
⚡ GIT MULTI-SYNC TOOL (v1.0.0) - SYSTEM INITIALIZATION
======================================================================
[INFO] Đang nạp cấu hình từ: /path/to/Application Support/git_sync/config.json
[INFO] Thư mục quét (scan_path): /Users/vic/_Work/zTool (Độ sâu tối đa: 3)

[1/2] 🔍 Đang quét đệ quy các thư mục chứa .git...
      ➔ Tìm thấy 5 repositories: git_sync, skills_sync, tools/tool_1, tools/tool_2, web_app.

[2/2] 🔄 Đang fetch và phân tích trạng thái Git (Song song)...
      [████████████████████████████████████████] 100% Hoàn tất!

======================================================================
```

---

## 2. Giao diện Menu chính & Bảng Dashboard CLI (Main CLI Dashboard Table)

Sau khi quét hoàn tất, in ra bảng dashboard sử dụng mã màu ANSI để làm nổi bật trạng thái:

*   **Màu xanh lá (Green):** Trạng thái `CLEAN` hoặc `UP_TO_DATE`.
*   **Màu đỏ (Red):** Trạng thái `DIRTY` hoặc `DIVERGED` (Cảnh báo nguy hiểm).
*   **Màu vàng (Yellow):** Trạng thái `BEHIND`, `AHEAD` hoặc `OFFLINE` (Cần đồng bộ hoặc kiểm tra mạng).
*   **Màu xám (Gray):** Trạng thái `NO_REMOTE`.

### Phiên bản giao diện Terminal:

```text
======================================================================
⚡ GIT MULTI-SYNC TOOL - CLI DASHBOARD
======================================================================
Thư mục quét (scan_path): /Users/vic/_Work/zTool (Độ sâu tối đa: 3)
Thời gian quét: 2.45s | Repositories: 5

┌─────────────────┬──────────┬──────────────┬──────────────┬─────────┬──────────────────────┐
│ Tên Dự Án       │ Nhánh    │ Trạng thái   │ Đồng bộ Git  │ Lệch    │ Hành động Đề xuất    │
├─────────────────┼──────────┼──────────────┼──────────────┼─────────┼──────────────────────┤
│ git_sync        │ main     │ CLEAN (Xanh) │ UP_TO_DATE   │ ▲0 | ▼0 │ Up-to-date           │
│ skills_sync     │ main     │ CLEAN (Xanh) │ AHEAD (Vàng) │ ▲2 | ▼0 │ Auto Push            │
│ tools/tool_1    │ develop  │ DIRTY (Đỏ)   │ BEHIND (Vàng)│ ▲0 | ▼3 │ Safe-Skip (Dirty)    │
│ web_app         │ feature  │ CLEAN (Xanh) │ BEHIND (Vàng)│ ▲0 | ▼1 │ Auto Pull            │
│ tools/tool_2    │ main     │ CLEAN (Xanh) │ DIVERGED (Đỏ)│ ▲1 | ▼1 │ Manual Merge Required│
└─────────────────┴──────────┴──────────────┴──────────────┴─────────┴──────────────────────┘

💡 GIẢI THÍCH MÃ MÀU:
   - ĐỎ: Có file sửa đổi chưa commit (Dirty) hoặc lệch nhánh phức tạp (Diverged).
   - VÀNG: Bị chậm hơn remote (Behind) hoặc có commit cục bộ chưa push (Ahead).
   - XANH LÁ: Sạch sẽ, đã đồng bộ mới nhất (Up-to-date).

VUI LÒNG CHỌN CHỨC NĂNG (Nhập số tương ứng rồi nhấn Enter):

  [1] Đồng bộ thông minh toàn bộ (Smart Sync All)
  [2] Chỉ Pull các Repo bị Behind (Smart Pull Only)
  [3] Chỉ Push các Repo bị Ahead (Smart Push Only)
  [4] Quét và làm mới trạng thái (Refresh status)
  [5] Thay đổi cấu hình quét (Edit config)
  [6] Thoát ứng dụng

Lựa chọn của bạn (1/2/3/4/5/6): _
```

---

## 3. Giao diện Thực thi Đồng bộ (Sync Execution Logs)

Khi người dùng chọn `1` (Smart Sync All):

```text
======================================================================
⚡ TIẾN TRÌNH ĐỒNG BỘ THÔNG MINH (SMART SYNC ACTIVE)
======================================================================

[1/3] Đồng bộ Repo: skills_sync (AHEAD)
      ➔ Đang chạy: git push origin main...
      [OK] Đã push thành công 2 commits lên remote branch.

[2/3] Đồng bộ Repo: web_app (BEHIND)
      ➔ Đang chạy: git pull --ff-only...
      [OK] Đã pull thành công 1 commit mới. Nhánh đã được fast-forward.

[3/3] Bỏ qua an toàn (Safe Skip):
      ⚠ blog_engine: Bị bỏ qua do Trạng thái Local là [DIRTY].
      ⚠ api_service: Bị bỏ qua do Trạng thái Git là [DIVERGED].

======================================================================
[INFO] ĐỒNG BỘ HOÀN TẤT!
- Đồng bộ thành công: 2 repositories.
- Bị bỏ qua an toàn: 2 repositories.
- Không cần đồng bộ: 1 repository.
======================================================================
Nhấn Enter để quay lại Dashboard...
```

---

## 4. Giao diện Thay đổi cấu hình (Submenu: Edit config)

Khi người dùng chọn `5` từ Menu chính:

```text
======================================================================
⚡ GIT MULTI-SYNC TOOL - CẤU HỒNG HỆ THỐNG
======================================================================
Đường dẫn file: /path/to/Application Support/git_sync/config.json

Cấu hình hiện tại:
  [1] Thư mục quét (scan_path): /Users/vic/_Work/zTool
  [2] Danh sách ignore (ignore_list): ["node_modules", "venv", ".venv"]
  [3] Độ sâu quét tối đa (max_depth): 3
  [4] Trở về Menu chính

Nhập số tương ứng để chỉnh sửa (1/2/3/4): 1

[SỬA THƯ MỤC QUÉT]
Nhập đường dẫn tuyệt đối mới (Ví dụ: /Users/vic/Projects): /Users/vic/_Work/another_workspace_
[OK] Đã lưu cấu hình mới thành công!
Nhấn Enter để quay lại...
```
