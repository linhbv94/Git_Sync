import asyncio
import time
import sys
import re
import os
import platform
import subprocess
from pathlib import Path
from typing import List, Tuple, Dict, Any
from src.config_manager import ConfigManager
from src.sync_engine import SyncEngine, GitStatusResult

# ANSI Color Codes
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
WHITE = "\033[37m"

LOCALIZED_UI = {
    "en": {
        "title": "⚡ GIT MULTI-SYNC TOOL - CLI DASHBOARD",
        "scan_path": "Workspace path (scan_path): {} (Max depth: {})",
        "scan_time": "Scanning time: {:.2f}s | Repositories: {}",
        "col_project": "Project Name",
        "col_branch": "Branch",
        "col_status": "File Status",
        "col_sync": "Git Sync",
        "col_offset": "Offset",
        "col_action": "Suggested Action",
        "legend": "💡 COLOR CODES EXPLANATION:\n   - RED: Uncommitted changes (Dirty) or Diverged branch.\n   - YELLOW: Behind remote (Behind) or Local commits unpushed (Ahead).\n   - GREEN: Clean and synchronized (Up-to-date).",
        "menu_title": "PLEASE SELECT FUNCTION (Enter option number and press Enter):",
        "menu_opt_1": "  [1] Smart Sync All (Pull BEHIND clean, Push AHEAD clean)",
        "menu_opt_2": "  [2] Smart Pull Only (Pull BEHIND clean)",
        "menu_opt_3": "  [3] Smart Push Only (Push AHEAD clean)",
        "menu_opt_4": "  [4] Scan and Refresh Status",
        "menu_opt_5": "  [5] Edit Scan Configuration",
        "menu_opt_6": "  [6] Open Config Folder",
        "menu_opt_7": "  [7] Exit Application",
        "prompt_choice": "Your choice (1-7): ",
        "suggest_up_to_date": "Up-to-date",
        "suggest_pull": "Auto Pull",
        "suggest_push": "Auto Push",
        "suggest_commit_push": "Auto Commit & Push",
        "suggest_diverged": "Manual Merge Required",
        "suggest_dirty": "Safe-Skip (Dirty)",
        "suggest_no_remote": "Link Remote Required",
        "suggest_offline": "Connection Warning",
        "suggest_auth": "Auth Warning",
        "scanning_wait": "\n🔍 Scanning and fetching remote branch info in background. Please wait...",
        "opening_folder": "\n📁 Opening configuration folder: {}",
        "config_submenu_title": "=== EDIT CONFIGURATION ===",
        "config_submenu_opt_1": "  [1] Change Scan Workspace Path (scan_path)",
        "config_submenu_opt_2": "  [2] Change Ignore List",
        "config_submenu_opt_3": "  [3] Change Max Scan Depth (max_depth)",
        "config_submenu_opt_4": "  [4] Change Display Language (lang)",
        "config_submenu_opt_5": "  [5] Back to Main Menu",
        "config_submenu_choice": "Your choice (1-5): ",
        "config_enter_new_path": "Enter new absolute path for scan_path: ",
        "config_enter_new_depth": "Enter new max depth (1-10): ",
        "config_depth_invalid": "❌ Invalid depth! Must be a number between 1 and 10.",
        "config_path_saved": "✅ New workspace path saved.",
        "config_depth_saved": "✅ New max depth saved.",
        "config_ignore_submenu": "\n--- IGNORE LIST CONFIGURATION ---\n[1] Add folder to ignore\n[2] Remove folder from ignore\n[3] Back\nChoice (1-3): ",
        "config_enter_add_ignore": "Enter folder name/path to add: ",
        "config_enter_remove_ignore": "Enter folder name/path to remove: ",
        "sync_active_title": "\n======================================================================\n⚡ SMART SYNC ACTIVE\n======================================================================",
        "sync_done": "\n✅ Sync execution completed! Press Enter to return to Dashboard...",
        "sync_item_start": "\n[{}/{}] Syncing repo: {} ({})",
        "sync_item_run": "      ➔ Running: {}",
        "sync_item_ok": "      [OK] {}",
        "sync_item_err": "      [ERR] {}",
        "sync_no_eligible": "\n💡 No repositories are eligible for safe synchronization."
    },
    "vi": {
        "title": "⚡ GIT MULTI-SYNC TOOL - CLI DASHBOARD",
        "scan_path": "Thư mục quét (scan_path): {} (Độ sâu tối đa: {})",
        "scan_time": "Thời gian quét: {:.2f}s | Repositories: {}",
        "col_project": "Tên Dự Án",
        "col_branch": "Nhánh",
        "col_status": "Trạng thái file",
        "col_sync": "Đồng bộ Git",
        "col_offset": "Lệch",
        "col_action": "Hành động Đề xuất",
        "legend": "💡 GIẢI THÍCH MÃ MÀU:\n   - ĐỎ: Có file sửa đổi chưa commit (Dirty) hoặc lệch nhánh phức tạp (Diverged).\n   - VÀNG: Bị chậm hơn remote (Behind) hoặc có commit cục bộ chưa push (Ahead).\n   - XANH LÁ: Sạch sẽ, đã đồng bộ mới nhất (Up-to-date).",
        "menu_title": "VUI LÒNG CHỌN CHỨC NĂNG (Nhập số tương ứng rồi nhấn Enter):",
        "menu_opt_1": "  [1] Đồng bộ thông minh toàn bộ (Smart Sync All)",
        "menu_opt_2": "  [2] Chỉ Pull các Repo bị Behind (Smart Pull Only)",
        "menu_opt_3": "  [3] Chỉ Push các Repo bị Ahead (Smart Push Only)",
        "menu_opt_4": "  [4] Quét và làm mới trạng thái (Refresh status)",
        "menu_opt_5": "  [5] Thay đổi cấu hình quét (Edit config)",
        "menu_opt_6": "  [6] Mở thư mục cấu hình (Open config folder)",
        "menu_opt_7": "  [7] Thoát ứng dụng",
        "prompt_choice": "Lựa chọn của bạn (1-7): ",
        "suggest_up_to_date": "Up-to-date",
        "suggest_pull": "Auto Pull",
        "suggest_push": "Auto Push",
        "suggest_commit_push": "Auto Commit & Push",
        "suggest_diverged": "Manual Merge Required",
        "suggest_dirty": "Safe-Skip (Dirty)",
        "suggest_no_remote": "Link Remote Required",
        "suggest_offline": "Connection Warning",
        "suggest_auth": "Auth Warning",
        "scanning_wait": "\n🔍 Đang quét và tìm nạp thông tin remote branch dưới nền. Vui lòng đợi...",
        "opening_folder": "\n📁 Đang mở thư mục chứa tệp cấu hình: {}",
        "config_submenu_title": "=== THAY ĐỔI CẤU HÌNH QUÉT ===",
        "config_submenu_opt_1": "  [1] Thay đổi thư mục quét (scan_path)",
        "config_submenu_opt_2": "  [2] Thay đổi danh sách bỏ qua (ignore_list)",
        "config_submenu_opt_3": "  [3] Thay đổi độ sâu quét tối đa (max_depth)",
        "config_submenu_opt_4": "  [4] Thay đổi ngôn ngữ hiển thị (lang)",
        "config_submenu_opt_5": "  [5] Quay lại Menu chính",
        "config_submenu_choice": "Lựa chọn của bạn (1-5): ",
        "config_enter_new_path": "Nhập đường dẫn tuyệt đối mới cho scan_path: ",
        "config_enter_new_depth": "Nhập độ sâu quét tối đa mới (1-10): ",
        "config_depth_invalid": "❌ Độ sâu không hợp lệ! Phải là số nguyên từ 1 đến 10.",
        "config_path_saved": "✅ Đã lưu thư mục quét mới thành công.",
        "config_depth_saved": "✅ Đã lưu độ sâu quét mới thành công.",
        "config_ignore_submenu": "\n--- CẤU HÌNH DANH SÁCH BỎ QUA ---\n[1] Thêm thư mục bỏ qua\n[2] Xóa thư mục khỏi danh sách bỏ qua\n[3] Quay lại\nLựa chọn (1-3): ",
        "config_enter_add_ignore": "Nhập tên/đường dẫn thư mục cần ignore: ",
        "config_enter_remove_ignore": "Nhập tên/đường dẫn thư mục cần xóa khỏi ignore: ",
        "sync_active_title": "\n======================================================================\n⚡ TIẾN TRÌNH ĐỒNG BỘ THÔNG MINH (SMART SYNC ACTIVE)\n======================================================================",
        "sync_done": "\n✅ Hoàn tất tiến trình đồng bộ! Nhấn Enter để quay lại Dashboard...",
        "sync_item_start": "\n[{}/{}] Đồng bộ Repo: {} ({})",
        "sync_item_run": "      ➔ Đang chạy: {}",
        "sync_item_ok": "      [OK] {}",
        "sync_item_err": "      [ERR] {}",
        "sync_no_eligible": "\n💡 Không có repository nào đủ điều kiện an toàn để đồng bộ."
    }
}

def visual_len(s: str) -> int:
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    return len(ansi_escape.sub('', s))

def pad_right(s: str, width: int) -> str:
    v_len = visual_len(s)
    if v_len >= width:
        return s
    return s + " " * (width - v_len)

def open_folder(path: Path) -> None:
    try:
        if platform.system() == "Darwin":
            subprocess.run(["open", str(path)])
        elif platform.system() == "Windows":
            os.startfile(path)
        else:
            subprocess.run(["xdg-open", str(path)])
    except Exception as e:
        print(f"❌ Cannot open folder: {e}")

class MainCLI:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.sync_engine = None
        self.lang = "en"
        self.ui = LOCALIZED_UI["en"]
        self.repos_status: List[Tuple[Path, GitStatusResult]] = []

    def initialize(self) -> None:
        if not self.config_manager.load_config():
            self.config_manager.run_onboarding()
            self.config_manager.load_config()
        
        cfg = self.config_manager.config
        self.lang = cfg.get("lang", "en")
        self.ui = LOCALIZED_UI.get(self.lang, LOCALIZED_UI["en"])
        
        self.sync_engine = SyncEngine(
            scan_path=cfg.get("scan_path", str(Path.cwd())),
            ignore_list=cfg.get("ignore_list", []),
            max_depth=cfg.get("max_depth", 3),
            timeout=cfg.get("timeout", 10),
            max_concurrency=cfg.get("max_concurrency", 8),
            lang=self.lang
        )

    def draw_dashboard(self, elapsed_time: float) -> None:
        print("\n" + "=" * 97)
        print(f"{CYAN}{BOLD}{self.ui['title']}{RESET}")
        print("=" * 97)
        print(self.ui["scan_path"].format(self.sync_engine.scan_path, self.sync_engine.max_depth))
        print(self.ui["scan_time"].format(elapsed_time, len(self.repos_status)))
        print()

        # Print Table Header
        header = (
            f"│ {pad_right(self.ui['col_project'], 18)} │ "
            f"{pad_right(self.ui['col_branch'], 12)} │ "
            f"{pad_right(self.ui['col_status'], 14)} │ "
            f"{pad_right(self.ui['col_sync'], 14)} │ "
            f"{pad_right(self.ui['col_offset'], 9)} │ "
            f"{pad_right(self.ui['col_action'], 22)} │"
        )
        print("┌" + "─" * 20 + "┬" + "─" * 14 + "┬" + "─" * 16 + "┬" + "─" * 16 + "┬" + "─" * 11 + "┬" + "─" * 24 + "┐")
        print(header)
        print("├" + "─" * 20 + "┼" + "─" * 14 + "┼" + "─" * 16 + "┼" + "─" * 16 + "┼" + "─" * 11 + "┼" + "─" * 24 + "┤")

        for path, status in self.repos_status:
            # Format relative project name
            try:
                proj_name = str(path.relative_to(self.sync_engine.scan_path))
            except ValueError:
                proj_name = path.name

            # Format File Status (Clean/Dirty)
            if status.is_dirty:
                status_str = f"{RED}DIRTY (Đỏ){RESET}"
            else:
                status_str = f"{GREEN}CLEAN (Xanh){RESET}"

            # Format Git Sync state and coloring
            sync_val = status.sync_state
            if sync_val == "UP_TO_DATE":
                sync_str = f"{GREEN}UP_TO_DATE{RESET}"
                action_str = self.ui["suggest_commit_push"] if status.is_dirty else self.ui["suggest_up_to_date"]
            elif sync_val == "BEHIND":
                sync_str = f"{YELLOW}BEHIND (Vàng){RESET}"
                action_str = self.ui["suggest_dirty"] if status.is_dirty else self.ui["suggest_pull"]
            elif sync_val == "AHEAD":
                sync_str = f"{YELLOW}AHEAD (Vàng){RESET}"
                action_str = self.ui["suggest_commit_push"] if status.is_dirty else self.ui["suggest_push"]
            elif sync_val == "DIVERGED":
                sync_str = f"{RED}DIVERGED (Đỏ){RESET}"
                action_str = self.ui["suggest_diverged"]
            elif sync_val == "NO_REMOTE":
                sync_str = f"{RED}NO_REMOTE (Đỏ){RESET}"
                action_str = self.ui["suggest_no_remote"]
            elif sync_val == "OFFLINE":
                sync_str = f"{RED}OFFLINE (Đỏ){RESET}"
                action_str = self.ui["suggest_offline"]
            elif sync_val == "AUTH_ERROR":
                sync_str = f"{RED}AUTH_ERROR (Đỏ){RESET}"
                action_str = self.ui["suggest_auth"]
            else:
                sync_str = f"{RED}ERROR (Đỏ){RESET}"
                action_str = status.error_message[:22]

            # Offset count
            offset_str = f"▲{status.ahead_count} | ▼{status.behind_count}"

            # Print Row
            row = (
                f"│ {pad_right(proj_name, 18)} │ "
                f"{pad_right(status.current_branch, 12)} │ "
                f"{pad_right(status_str, 14)} │ "
                f"{pad_right(sync_str, 14)} │ "
                f"{pad_right(offset_str, 9)} │ "
                f"{pad_right(action_str, 22)} │"
            )
            print(row)

        print("└" + "─" * 20 + "┴" + "─" * 14 + "┴" + "─" * 16 + "┴" + "─" * 16 + "┴" + "─" * 11 + "┴" + "─" * 24 + "┘")
        print(self.ui["legend"])
        print()

    def edit_config_menu(self) -> None:
        while True:
            print("\n" + "=" * 40)
            print(f"{CYAN}{BOLD}{self.ui['config_submenu_title']}{RESET}")
            print("=" * 40)
            print(self.ui["config_submenu_opt_1"])
            print(self.ui["config_submenu_opt_2"])
            print(self.ui["config_submenu_opt_3"])
            print(self.ui["config_submenu_opt_4"])
            print(self.ui["config_submenu_opt_5"])
            print()
            choice = input(self.ui["config_submenu_choice"]).strip()
            
            if choice == "1":
                new_path = input(self.ui["config_enter_new_path"]).strip()
                if new_path:
                    p = Path(new_path).expanduser().resolve()
                    if p.exists() and p.is_dir():
                        self.config_manager.config["scan_path"] = str(p)
                        self.config_manager.save_config()
                        self.sync_engine.scan_path = p
                        print(f"\n{GREEN}{self.ui['config_path_saved']}{RESET}")
                    else:
                        print(f"\n{RED}❌ Workspace path does not exist!{RESET}")
            
            elif choice == "2":
                self.edit_ignore_list_menu()
            
            elif choice == "3":
                new_depth = input(self.ui["config_enter_new_depth"]).strip()
                if new_depth.isdigit():
                    depth = int(new_depth)
                    if 1 <= depth <= 10:
                        self.config_manager.config["max_depth"] = depth
                        self.config_manager.save_config()
                        self.sync_engine.max_depth = depth
                        print(f"\n{GREEN}{self.ui['config_depth_saved']}{RESET}")
                    else:
                        print(f"\n{RED}{self.ui['config_depth_invalid']}{RESET}")
                else:
                    print(f"\n{RED}{self.ui['config_depth_invalid']}{RESET}")
            
            elif choice == "4":
                # Change display language
                while True:
                    lang_choice = input("\nVui lòng chọn ngôn ngữ hiển thị / Please select display language:\n  [1] English (en)\n  [2] Tiếng Việt (vi)\n\nLựa chọn / Choice (1/2): ").strip()
                    if lang_choice == "1":
                        new_lang = "en"
                        break
                    elif lang_choice == "2":
                        new_lang = "vi"
                        break
                    else:
                        print("❌ Invalid choice! Vui lòng nhập lại.")
                
                self.config_manager.config["lang"] = new_lang
                self.config_manager.save_config()
                self.lang = new_lang
                self.ui = LOCALIZED_UI[new_lang]
                self.sync_engine.lang = new_lang
                print(f"\n{GREEN}✅ Language updated / Ngôn ngữ đã được cập nhật.{RESET}")
            
            elif choice == "5":
                break

    def edit_ignore_list_menu(self) -> None:
        while True:
            ignore_list = self.config_manager.config.setdefault("ignore_list", [])
            print(f"\n[DANH SÁCH BỎ QUA HIỆN TẠI]: {ignore_list}")
            choice = input(self.ui["config_ignore_submenu"]).strip()
            if choice == "1":
                folder = input(self.ui["config_enter_add_ignore"]).strip()
                if folder and folder not in ignore_list:
                    ignore_list.append(folder)
                    self.config_manager.save_config()
                    self.sync_engine.ignore_list = ignore_list
            elif choice == "2":
                folder = input(self.ui["config_enter_remove_ignore"]).strip()
                if folder in ignore_list:
                    ignore_list.remove(folder)
                    self.config_manager.save_config()
                    self.sync_engine.ignore_list = ignore_list
            elif choice == "3":
                break

    async def scan_and_refresh(self) -> float:
        print(self.ui["scanning_wait"])
        start_time = time.time()
        
        # Scan workspace
        repo_paths = self.sync_engine.scan_workspace()
        
        # Concurrently check statuses
        self.repos_status = await self.sync_engine.check_all_repos(repo_paths)
        
        # Sort by project name
        self.repos_status.sort(key=lambda x: x[0].name)
        
        return time.time() - start_time

    async def run_sync_action(self, action_type: str) -> None:
        print(self.ui["sync_active_title"])
        
        # Find active tasks
        tasks = []
        for path, status in self.repos_status:
            if status.is_dirty:
                # If dirty and behind_count == 0, we can run commit & push
                if status.behind_count == 0 and status.sync_state in ("UP_TO_DATE", "AHEAD"):
                    if action_type in ("ALL", "PUSH"):
                        tasks.append((path, "COMMIT_PUSH", status.current_branch))
                continue
            
            if action_type in ("ALL", "PULL") and status.sync_state == "BEHIND":
                tasks.append((path, "PULL", status.current_branch))
            elif action_type in ("ALL", "PUSH") and status.sync_state == "AHEAD":
                tasks.append((path, "PUSH", status.current_branch))
        
        if not tasks:
            print(self.ui["sync_no_eligible"])
            input(self.ui["sync_done"])
            return

        # Perform sync sequentially with clean logging
        for idx, (path, act, branch) in enumerate(tasks, 1):
            proj_name = path.name
            try:
                proj_name = str(path.relative_to(self.sync_engine.scan_path))
            except ValueError:
                pass
            print(self.ui["sync_item_start"].format(idx, len(tasks), proj_name, act))
            
            if act == "PULL":
                cmd = f"git pull --ff-only origin {branch}"
                print(self.ui["sync_item_run"].format(cmd))
                success, msg = await asyncio.to_thread(self.sync_engine.git_engine.execute_smart_pull, path, branch, self.lang)
            elif act == "PUSH":
                cmd = f"git push origin {branch}"
                print(self.ui["sync_item_run"].format(cmd))
                success, msg = await asyncio.to_thread(self.sync_engine.git_engine.execute_smart_push, path, branch, self.lang)
            elif act == "COMMIT_PUSH":
                cmd = f"git add . && git commit -m \"auto sync: local updates\" && git push origin {branch}"
                print(self.ui["sync_item_run"].format(cmd))
                success, msg = await asyncio.to_thread(self.sync_engine.git_engine.execute_commit_and_push, path, branch, self.lang)
            
            if success:
                print(f"{GREEN}{self.ui['sync_item_ok'].format(msg)}{RESET}")
            else:
                print(f"{RED}{self.ui['sync_item_err'].format(msg)}{RESET}")

        input(self.ui["sync_done"])

    async def main_loop(self) -> None:
        self.initialize()
        
        elapsed = await self.scan_and_refresh()
        
        while True:
            self.draw_dashboard(elapsed)
            print(self.ui["menu_title"])
            print(self.ui["menu_opt_1"])
            print(self.ui["menu_opt_2"])
            print(self.ui["menu_opt_3"])
            print(self.ui["menu_opt_4"])
            print(self.ui["menu_opt_5"])
            print(self.ui["menu_opt_6"])
            print(self.ui["menu_opt_7"])
            print()
            
            choice = input(self.ui["prompt_choice"]).strip()
            
            if choice == "1":
                await self.run_sync_action("ALL")
                elapsed = await self.scan_and_refresh()
            elif choice == "2":
                await self.run_sync_action("PULL")
                elapsed = await self.scan_and_refresh()
            elif choice == "3":
                await self.run_sync_action("PUSH")
                elapsed = await self.scan_and_refresh()
            elif choice == "4":
                elapsed = await self.scan_and_refresh()
            elif choice == "5":
                self.edit_config_menu()
                elapsed = await self.scan_and_refresh()
            elif choice == "6":
                print(self.ui["opening_folder"].format(self.config_manager.config_dir))
                open_folder(self.config_manager.config_dir)
            elif choice == "7":
                # Close front Terminal window on macOS or Command window on Windows
                system = platform.system()
                if system == "Darwin":
                    subprocess.Popen(["osascript", "-e", 'tell application "Terminal" to close front window'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                elif system == "Windows":
                    try:
                        import ctypes
                        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
                        if hwnd != 0:
                            ctypes.windll.user32.PostMessageW(hwnd, 0x0010, 0, 0)
                    except Exception:
                        pass
                sys.exit(0)

def main():
    try:
        asyncio.run(MainCLI().main_loop())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)

if __name__ == "__main__":
    main()
