import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List

class ConfigManager:
    def __init__(self):
        self.config_dir = self._get_config_dir()
        self.config_path = self.config_dir / "config.json"
        self.config: Dict[str, Any] = {}

    def _get_config_dir(self) -> Path:
        home = Path.home()
        if sys.platform == "darwin":
            return home / "Library" / "Application Support" / "Git_Sync"
        elif sys.platform == "win32":
            appdata = os.environ.get("APPDATA")
            if appdata:
                return Path(appdata) / "Git_Sync"
            return home / "AppData" / "Roaming" / "Git_Sync"
        else:
            return home / ".config" / "Git_Sync"

    def load_config(self) -> bool:
        """Loads config.json. Returns True if exists and loaded successfully, otherwise False."""
        if not self.config_path.exists():
            return False
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)
            # Populate defaults if missing
            self.config.setdefault("max_depth", 3)
            self.config.setdefault("timeout", 10)
            self.config.setdefault("max_concurrency", 8)
            return True
        except Exception:
            return False

    def save_config(self) -> None:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    def run_onboarding(self) -> None:
        """Interactive Onboarding Flow for initial configuration."""
        print("======================================================================")
        print("⚡ GIT MULTI-SYNC TOOL - CẤU HÌNH BAN ĐẦU / INITIAL SETUP")
        print("======================================================================")
        print("💡 config.json không tồn tại. Bắt đầu thiết lập ban đầu.")
        print("💡 config.json not found. Starting initial configuration.")
        print()

        # Step 1: Language selection
        lang = "en"
        while True:
            choice = input("Vui lòng chọn ngôn ngữ hiển thị / Please select display language:\n  [1] English (en)\n  [2] Tiếng Việt (vi)\n\nLựa chọn của bạn / Your choice (1/2): ").strip()
            if choice == "1":
                lang = "en"
                break
            elif choice == "2":
                lang = "vi"
                break
            else:
                print("\n❌ Lựa chọn không hợp lệ! Invalid choice! Vui lòng nhập lại / Please re-enter.\n")

        self.config["lang"] = lang

        # Define localization strings
        if lang == "vi":
            prompt_scan_path = "\n💡 Vui lòng nhập đường dẫn tuyệt đối đến Thư mục cha (Workspace) cần quét.\n(Nhấn Enter trực tiếp để mặc định lấy thư mục hiện tại: {})\n\nNhập đường dẫn: "
            err_path_not_exist = "\n❌ Đường dẫn không tồn tại! Vui lòng kiểm tra lại."
            prompt_ignore = "\n💡 Vui lòng nhập tên thư mục hoặc đường dẫn cần bỏ qua khi quét (ignore_list).\n(Nhấn Enter trực tiếp trên dòng trống để HOÀN TẤT cấu hình).\n"
            current_ignore_msg = "[DANH SÁCH BỎ QUA HIỆN TẠI]: {}"
            input_ignore_next = "Nhập thư mục cần ignore tiếp theo (nhấn Enter để xong): "
            added_msg = "➔ Đã thêm '{}' vào danh sách bỏ qua."
            done_msg = "\n[INFO] Cấu hình Onboarding hoàn tất! Đang vào Dashboard...\n"
        else:
            prompt_scan_path = "\n💡 Please enter the absolute path to the Parent directory (Workspace) to scan.\n(Press Enter directly to use current directory: {})\n\nEnter path: "
            err_path_not_exist = "\n❌ Path does not exist! Please check again."
            prompt_ignore = "\n💡 Please enter directory name or path to ignore during scanning (ignore_list).\n(Press Enter directly on an empty line to COMPLETE configuration).\n"
            current_ignore_msg = "[CURRENT IGNORE LIST]: {}"
            input_ignore_next = "Enter the next directory to ignore (press Enter to finish): "
            added_msg = "➔ Added '{}' to ignore list."
            done_msg = "\n[INFO] Onboarding configuration completed! Loading Dashboard...\n"

        # Step 2: Scan path selection
        # Smart default path resolution (avoid defaulting to User Home if launched from Finder/Terminal defaults)
        if getattr(sys, 'frozen', False):
            base_path = Path(sys.executable).resolve()
        else:
            base_path = Path(__file__).resolve()
        
        # Climb up to find the root folder of the git_sync tool
        tool_dir = base_path.parent if base_path.is_file() else base_path
        while tool_dir.name.lower() in ("dist", "src") or tool_dir.suffix.lower() in (".py", ".exe"):
            if tool_dir == tool_dir.parent:
                break
            tool_dir = tool_dir.parent
        
        # Default scan path is the parent workspace containing git_sync / git_multi_sync (e.g. zTools)
        if tool_dir.name.lower() in ("git_sync", "git-sync", "git_auto_sync", "git-auto-sync", "git_multi_sync", "git-multi-sync") and tool_dir.parent != tool_dir:
            default_dir = tool_dir.parent
        else:
            default_dir = tool_dir
        
        # Fallback to home if default_dir is root
        if default_dir == Path("/"):
            default_dir = Path.home()
            
        while True:
            scan_path_input = input(prompt_scan_path.format(default_dir)).strip()
            if not scan_path_input:
                scan_path = str(default_dir)
                break
            else:
                p = Path(scan_path_input).expanduser().resolve()
                if p.exists() and p.is_dir():
                    scan_path = str(p)
                    break
                else:
                    print(err_path_not_exist)

        self.config["scan_path"] = scan_path

        # Step 3: Interactive ignore loop
        print(prompt_ignore)
        ignore_list = ["node_modules", "venv", ".venv", "build", "dist"]
        while True:
            print(current_ignore_msg.format(json.dumps(ignore_list)))
            ignore_input = input(input_ignore_next).strip()
            if not ignore_input:
                break
            else:
                if ignore_input not in ignore_list:
                    ignore_list.append(ignore_input)
                    print(added_msg.format(ignore_input))
                print()

        self.config["ignore_list"] = ignore_list
        self.config["max_depth"] = 3
        self.config["timeout"] = 10
        self.config["max_concurrency"] = 8

        # Step 4: Save configuration
        self.save_config()
        print(done_msg)
