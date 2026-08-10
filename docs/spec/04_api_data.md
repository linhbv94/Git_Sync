# Data & API Specification: Git Multi-Sync Tool (`_spec4_api_data`)

> **Version:** 1.0.0  
> **Last Updated:** 2026-08-10  
> **Target Audience:** Backend Dev, System Architect, Test Agent  

---

## 1. Schema Tệp Cấu hình `config.json`

File cấu hình được lưu tập trung tại thư mục AppData hệ thống để tránh bị ghi đè khi cập nhật code:
- **macOS:** `~/Library/Application Support/git_sync/config.json`
- **Windows:** `%APPDATA%\git_sync\config.json`

### JSON Schema Specification:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "GitMultiSyncConfig",
  "type": "object",
  "properties": {
    "scan_path": {
      "type": "string",
      "description": "Đường dẫn tuyệt đối đến thư mục chứa các repositories cần quét. Nếu để rỗng, tool sẽ mặc định dùng thư mục mẹ của tool."
    },
    "ignore_list": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "Danh sách các tên thư mục con cần bỏ qua không quét (ví dụ: node_modules, venv...)."
    },
    "max_depth": {
      "type": "integer",
      "minimum": 1,
      "maximum": 5,
      "default": 3,
      "description": "Độ sâu đệ quy tối đa khi tìm kiếm thư mục chứa .git/."
    },
    "timeout": {
      "type": "integer",
      "minimum": 3,
      "maximum": 60,
      "default": 10,
      "description": "Thời gian chờ tối đa (giây) cho một tiến trình git subprocess (fetch, pull, push) trước khi tự hủy tiến trình đó."
    },
    "max_concurrency": {
      "type": "integer",
      "minimum": 1,
      "maximum": 32,
      "default": 8,
      "description": "Số lượng luồng fetch/status được thực thi song song tối đa."
    }
  },
  "required": ["scan_path", "ignore_list", "max_depth", "timeout", "max_concurrency"]
}
```

### Ví dụ tệp cấu hình hợp lệ:

```json
{
  "scan_path": "/Users/vic/_Work/zTool",
  "ignore_list": [
    "node_modules",
    "venv",
    ".venv",
    "build",
    "dist",
    "temp_repo"
  ],
  "max_depth": 3,
  "timeout": 10,
  "max_concurrency": 8
}
```

---

## 2. Cấu trúc Mô hình Dữ liệu Bộ nhớ (Internal Memory Data Structure)

Để quản lý và hiển thị danh sách repositories, Sync Engine sử dụng lớp mô hình dữ liệu (Dataclass trong Python):

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

@dataclass
class GitRepoInfo:
    name: str                           # Đường dẫn tương đối từ scan_path (ví dụ: "tools/tool_1" hoặc "skills_sync")
    path: Path                          # Đường dẫn Path tuyệt đối cục bộ
    current_branch: str = "main"        # Tên branch đang checkout cục bộ
    is_dirty: bool = False              # True nếu working tree có file sửa đổi chưa commit
    dirty_files: List[str] = field(default_factory=list) # Danh sách file dirty
    sync_state: str = "UNRESOLVED"      # "UP_TO_DATE", "BEHIND", "AHEAD", "DIVERGED", "NO_REMOTE", "OFFLINE_ERROR"
    ahead_count: int = 0                # Số commit ahead so với upstream
    behind_count: int = 0               # Số commit behind so với upstream
    remote_url: Optional[str] = None    # Địa chỉ git remote origin URL
    error_message: str = ""             # Chi tiết thông báo lỗi nếu có (ví dụ lỗi auth, lỗi merge)
```

---

## 3. Cấu trúc Payload kết quả tiến trình (Sync Action Report Schema)

Sau khi hoàn tất hành động đồng bộ thông minh, engine trả về một payload báo cáo trạng thái tổng để in ra Dashboard:

```python
@dataclass
class SyncReportSummary:
    scanned_count: int = 0
    synced_pull_count: int = 0
    synced_push_count: int = 0
    skipped_dirty_count: int = 0
    skipped_diverged_count: int = 0
    failed_count: int = 0
    execution_time_seconds: float = 0.0
```
