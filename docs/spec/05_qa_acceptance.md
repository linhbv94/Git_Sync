# QA & Acceptance Specification: Git Multi-Sync Tool (`_spec5_qa_acceptance`)

> **Version:** 1.0.0  
> **Last Updated:** 2026-08-10  
> **Target Audience:** QA/QC, Test Agent, Dev Agent  

---

## 1. Tiêu chí Nghiệm thu định dạng Gherkin (Acceptance Criteria)

Các kịch bản kiểm thử hành vi cốt lõi phục vụ viết test cases tự động và kiểm thử thủ công:

### Kịch bản 0: Thiết lập Onboarding ban đầu (Interactive setup loop)
```gherkin
Given hệ thống chưa có tệp cấu hình config.json lưu trong AppData / Application Support
When người dùng khởi động chương trình
Then chương trình hiển thị màn hình chọn ngôn ngữ chào mừng
When người dùng chọn phím `2` (Tiếng Việt)
Then chương trình lưu ngôn ngữ hiển thị và yêu cầu nhập scan_path
When người dùng nhấn Enter để bỏ qua scan_path
Then chương trình gán scan_path là thư mục hiện tại và yêu cầu nhập danh sách ignore
When người dùng nhập `tools/temp_dir` và nhấn Enter
Then chương trình thêm `tools/temp_dir` vào danh sách ignore hiện tại
And in ra danh sách ignore cập nhật gồm `["node_modules", "venv", ".venv", "build", "dist", "tools/temp_dir"]`
And tiếp tục nhắc người dùng nhập thư mục ignore tiếp theo
When người dùng nhấn Enter trực tiếp trên dòng trống
Then chương trình kết thúc vòng lặp
And lưu cấu hình `config.json` hệ thống với:
  - `lang`: "vi"
  - `scan_path`: "/Users/vic/_Work/zTool"
  - `ignore_list`: ["node_modules", "venv", ".venv", "build", "dist", "tools/temp_dir"]
  - `max_depth`: 3
  - `timeout`: 10
  - `max_concurrency`: 8
And chuyển tiếp trực tiếp vào màn hình Dashboard chính
```

### Kịch bản 1: Quét đệ quy và liệt kê các repo cục bộ thành công
```gherkin
Given hệ thống đã cài đặt Git CLI và người dùng có file config.json hợp lệ với `max_depth = 3`
And thư mục quét `/Users/vic/_Work/zTool` chứa:
  - 2 Git repos cấp 1: `git_sync` và `skills_sync`
  - 1 thư mục `tools` chứa 2 Git repos cấp 2: `tools/tool_1` và `tools/tool_2`
When người dùng khởi động chương trình
Then chương trình thực hiện quét đệ quy tìm kiếm
And hiển thị bảng danh sách Dashboard gồm 4 hàng tương ứng với: `git_sync`, `skills_sync`, `tools/tool_1`, và `tools/tool_2`
And hiển thị đúng tên branch hiện tại đang được checkout ở mỗi repo
```

### Kịch bản 2: Smart Sync tự động Pull đối với repo BEHIND đang sạch (CLEAN)
```gherkin
Given repo `web_app` đang checkout branch `main`
And trạng thái file là CLEAN (không có file sửa đổi chưa commit)
And trạng thái so sánh với remote là BEHIND (lệch commit: ▲0 | ▼2)
When người dùng chọn phím `1` (Smart Sync All) trên Menu
Then chương trình thực thi lệnh `git pull --ff-only` trên repo `web_app`
And in thông báo thành công: `[OK] Đã pull thành công 2 commits mới`
And trạng thái của repo `web_app` chuyển sang `UP_TO_DATE` trên Dashboard
```

### Kịch bản 3: Smart Sync tự động Push đối với repo AHEAD đang sạch (CLEAN)
```gherkin
Given repo `skills_sync` đang checkout branch `main`
And trạng thái file là CLEAN
And trạng thái so sánh với remote là AHEAD (lệch commit: ▲3 | ▼0)
When người dùng chọn phím `1` (Smart Sync All) trên Menu
Then chương trình thực thi lệnh `git push origin main` trên repo `skills_sync`
And in thông báo thành công: `[OK] Đã push thành công 3 commits lên remote`
And trạng thái của repo `skills_sync` chuyển sang `UP_TO_DATE` trên Dashboard
```

### Kịch bản 4: Chặn tự động đồng bộ (Safe-Skip) khi repo bị bẩn (DIRTY)
```gherkin
Given repo `tools/tool_1` đang ở trạng thái DIRTY (có tệp tin `index.html` chưa commit)
And trạng thái so sánh là BEHIND (lệch commit: ▲0 | ▼3)
When người dùng chọn phím `1` (Smart Sync All) trên Menu
Then chương trình không thực thi bất kỳ lệnh git pull hay push nào trên repo `tools/tool_1`
And in cảnh báo màu vàng/đỏ: `tools/tool_1: Bị bỏ qua do Trạng thái Local là [DIRTY]`
And mã nguồn cục bộ của `tools/tool_1` được giữ nguyên vẹn
```

### Kịch bản 5: Chặn tự động đồng bộ khi repo bị Diverged (Phân nhánh lệch commit cả 2 phía)
```gherkin
Given repo `tools/tool_2` đang ở trạng thái CLEAN
And trạng thái so sánh là DIVERGED (lệch commit: ▲1 | ▼1)
When người dùng chọn phím `1` (Smart Sync All) trên Menu
Then chương trình không thực thi git pull hay git push
And in cảnh báo: `tools/tool_2: Bị bỏ qua do Trạng thái Git là [DIVERGED]`
And ghi nhận log yêu cầu người dùng xử lý xung đột bằng tay (Manual merge required)
```

### Kịch bản 6: Mở thư mục chứa tệp cấu hình hệ thống
```gherkin
Given người dùng đang ở giao diện Dashboard chính
When người dùng chọn phím `6` (Mở thư mục cấu hình)
Then chương trình khởi chạy lệnh mở thư mục hệ thống tương ứng (open/explorer)
And hiển thị cửa sổ Explorer/Finder trỏ tới thư mục chứa tệp cấu hình hệ thống
And Dashboard chính tiếp tục hiển thị và chờ người dùng nhập lệnh tiếp theo
```

---

## 2. Ma trận Edge Cases & Validation Rules

| ID | Tình huống Biên / Ngoại lệ (Edge Case) | Tác động | Giải pháp Xử lý của Sync Engine |
| :--- | :--- | :--- | :--- |
| **EC-01** | Máy tính chưa cài đặt Git CLI | Treo app / Lỗi runtime | Chương trình kiểm tra lệnh `git` ngay khi khởi chạy. Nếu lỗi, in banner thông báo đỏ: *Git CLI chưa được cài đặt. Vui lòng tải về từ git-scm.com.* và thoát app an toàn. |
| **EC-02** | Thư mục cấu hình quét `scan_path` không tồn tại | Lỗi quét thư mục | Chương trình tự động kiểm tra `Path(scan_path).exists()`. Nếu không tồn tại, in thông báo cảnh báo và tự động fallback về thư mục hiện hành (`./`). |
| **EC-03** | Lỗi xác thực Git Remote (Token hết hạn hoặc sai SSH Key) | Chờ nhập mật khẩu làm treo tiến trình | Gán biến môi trường `GIT_TERMINAL_PROMPT=0` để ngắt prompt. Nếu git fetch trả về exit code != 0 và stderr chứa `Permission denied`, đánh dấu trạng thái repo là `AUTH_ERROR` và hiển thị cảnh báo đỏ trên dashboard. |
| **EC-04** | Kết nối internet bị ngắt giữa chừng | Fetch hoặc Sync bị đơ | Thiết lập timeout cho subprocess tối đa 10 giây. Nếu bị ngắt kết nối mạng, gán trạng thái repo là `OFFLINE_ERROR` và tiếp tục xử lý các repo khác (không làm đổ vỡ cả chương trình). |
| **EC-05** | Nhánh hiện tại cục bộ chưa có upstream remote tương ứng | Không thể pull/push | Đánh dấu trạng thái repo là `NO_REMOTE` (màu xám) và bỏ qua an toàn không sync. |
| **EC-06** | Thư mục quét hoàn toàn không có Git repo nào | Bảng dashboard trống rỗng | In ra thông báo: *Không tìm thấy Git repository nào trong thư mục quét của bạn.* và đề xuất sửa config. |
| **EC-07** | Repository lồng sâu hơn `max_depth` cấu hình | Repo không được hiển thị | Đệ quy bỏ qua các thư mục con ở cấp độ sâu lớn hơn `max_depth`, không đưa vào kết quả quét. |
