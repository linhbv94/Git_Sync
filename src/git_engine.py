import subprocess
import shutil
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Any, Optional

GIT_LOCALIZED = {
    "en": {
        "no_git_cli": "Git CLI is not installed.",
        "no_git_repo": "Not a Git repository.",
        "no_remote": "No remote configured.",
        "auth_err": "Git Remote Auth Error (Check Token or SSH key): {}",
        "offline": "No internet connection (Offline).",
        "not_found": "Remote repository not found.",
        "pull_ok": "Successfully pulled updates.",
        "pull_ff_err": "Cannot auto pull fast-forward: {}",
        "push_ok": "Successfully pushed changes.",
        "push_err": "Cannot push to remote: {}",
        "timeout": "Operation timed out.",
        "unknown_err": "Unknown error: {}"
    },
    "vi": {
        "no_git_cli": "Git CLI chưa được cài đặt.",
        "no_git_repo": "Không phải thư mục Git repo.",
        "no_remote": "Chưa cấu hình remote origin.",
        "auth_err": "Lỗi xác thực Git Remote (Chưa cấu hình Token hoặc SSH key): {}",
        "offline": "Không có kết nối mạng (Offline).",
        "not_found": "Không tìm thấy repository trên Remote.",
        "pull_ok": "Đã pull dữ liệu mới thành công.",
        "pull_ff_err": "Không thể auto pull fast-forward: {}",
        "push_ok": "Đã push dữ liệu mới thành công.",
        "push_err": "Không thể push lên remote: {}",
        "timeout": "Lệnh thực thi bị quá thời gian.",
        "unknown_err": "Lỗi không xác định: {}"
    }
}

@dataclass
class GitStatusResult:
    sync_state: str  # "UP_TO_DATE", "BEHIND", "AHEAD", "DIVERGED", "NO_REMOTE", "OFFLINE", "AUTH_ERROR", "ERROR"
    is_dirty: bool
    current_branch: str = "main"
    ahead_count: int = 0
    behind_count: int = 0
    dirty_files: List[str] = field(default_factory=list)
    error_message: str = ""

class GitEngine:
    """Invokes Git shell commands for analyzing and syncing individual repositories."""

    @staticmethod
    def is_git_available() -> bool:
        return shutil.which("git") is not None

    def run_cmd(self, args: List[str], cwd: Path, timeout: int = 15) -> Tuple[int, str, str]:
        """Safely runs a Git subprocess, suppressing interactive prompts."""
        try:
            env = os.environ.copy()
            env["GIT_TERMINAL_PROMPT"] = "0"
            env["GIT_SSH_COMMAND"] = "ssh -o BatchMode=yes"
            res = subprocess.run(
                ["git"] + args,
                cwd=cwd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
                timeout=timeout
            )
            return res.returncode, res.stdout.strip(), res.stderr.strip()
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
        except Exception as e:
            return -1, "", str(e)

    def get_current_branch(self, repo_path: Path) -> str:
        code, out, _ = self.run_cmd(["branch", "--show-current"], cwd=repo_path)
        if code == 0 and out:
            return out
        # Fallback to symbolic name
        code, out, _ = self.run_cmd(["rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_path)
        if code == 0 and out:
            return out
        return "HEAD"

    def resolve_remote_name(self, repo_path: Path, branch: str) -> Optional[str]:
        # 1. Check if the current branch has a tracking remote configured
        code, out, _ = self.run_cmd(["config", "--get", f"branch.{branch}.remote"], cwd=repo_path)
        if code == 0 and out.strip():
            return out.strip()
        
        # 2. Check if remote 'origin' exists
        code, out, _ = self.run_cmd(["remote"], cwd=repo_path)
        if code == 0 and out:
            remotes = [r.strip() for r in out.splitlines() if r.strip()]
            if "origin" in remotes:
                return "origin"
            # 3. Use the first available remote
            if remotes:
                return remotes[0]
        return None

    def get_remote_url(self, repo_path: Path, remote_name: str) -> str:
        code, out, _ = self.run_cmd(["remote", "get-url", remote_name], cwd=repo_path)
        if code == 0 and out:
            return out.strip()
        return ""

    def fetch_remote(self, repo_path: Path, remote_name: str, branch: str, lang: str = "en", timeout: int = 10) -> Tuple[bool, str, str]:
        """Runs git fetch <remote_name> <branch>. Returns (success, error_type, error_msg)."""
        l = GIT_LOCALIZED.get(lang, GIT_LOCALIZED["en"])
        code, out, err = self.run_cmd(["fetch", remote_name, branch], cwd=repo_path, timeout=timeout)
        if code == 0:
            return True, "", ""
        
        err_lower = err.lower()
        if "timeout" in err_lower:
            return False, "TIMEOUT", l["timeout"]
        elif any(x in err_lower for x in ["auth", "permission denied", "could not read username", "terminal prompts disabled"]):
            return False, "AUTH", l["auth_err"].format(err)
        elif any(x in err_lower for x in ["could not resolve host", "network is unreachable", "connection reset", "timed out"]):
            return False, "OFFLINE", l["offline"]
        elif "not found" in err_lower or "does not appear to be a git repository" in err_lower:
            return False, "NOT_FOUND", l["not_found"]
        
        return False, "ERROR", l["unknown_err"].format(err)

    def get_git_status(self, repo_path: Path, lang: str = "en", timeout: int = 10) -> GitStatusResult:
        l = GIT_LOCALIZED.get(lang, GIT_LOCALIZED["en"])
        if not self.is_git_available():
            return GitStatusResult(sync_state="ERROR", is_dirty=False, error_message=l["no_git_cli"])
        
        if not (repo_path / ".git").exists():
            return GitStatusResult(sync_state="ERROR", is_dirty=False, error_message=l["no_git_repo"])

        branch = self.get_current_branch(repo_path)
        remote_name = self.resolve_remote_name(repo_path, branch)
        remote_url = self.get_remote_url(repo_path, remote_name) if remote_name else ""

        # Check working tree status (Dirty or Clean)
        code, status_out, _ = self.run_cmd(["status", "--porcelain"], cwd=repo_path)
        dirty_files = []
        for line in status_out.splitlines():
            line_str = line.strip()
            if not line_str:
                continue
            # Filter out system files (.DS_Store / Thumbs.db) from marking the repo as dirty
            parts = line_str.split(None, 1)
            if len(parts) >= 2:
                filename = parts[1].strip()
                if filename.endswith(".DS_Store") or filename.endswith("Thumbs.db"):
                    continue
            dirty_files.append(line_str)
        is_dirty = len(dirty_files) > 0

        if not remote_url or not remote_name:
            return GitStatusResult(
                sync_state="NO_REMOTE",
                is_dirty=is_dirty,
                current_branch=branch,
                dirty_files=dirty_files,
                error_message=l["no_remote"]
            )

        # Try to fetch
        fetch_success, err_type, err_msg = self.fetch_remote(repo_path, remote_name, branch, lang, timeout)

        if not fetch_success:
            if err_type in ("OFFLINE", "TIMEOUT"):
                state = "OFFLINE"
            elif err_type == "AUTH":
                state = "AUTH_ERROR"
            else:
                state = "ERROR"
            
            return GitStatusResult(
                sync_state=state,
                is_dirty=is_dirty,
                current_branch=branch,
                dirty_files=dirty_files,
                error_message=err_msg
            )

        # Compare HEAD with <remote_name>/<branch>
        code, rev_out, _ = self.run_cmd(["rev-list", "--left-right", "--count", f"HEAD...{remote_name}/{branch}"], cwd=repo_path)
        
        ahead = 0
        behind = 0
        if code == 0 and rev_out:
            parts = rev_out.split()
            if len(parts) >= 2:
                ahead = int(parts[0])
                behind = int(parts[1])
        else:
            # If the branch does not exist on remote yet, it's a new local branch.
            # We can check if remote_name/branch exists
            check_code, _, _ = self.run_cmd(["rev-parse", "--verify", f"{remote_name}/{branch}"], cwd=repo_path)
            if check_code != 0:
                # Remote branch doesn't exist ➔ ahead by current local commits
                commit_code, commit_count, _ = self.run_cmd(["rev-list", "--count", "HEAD"], cwd=repo_path)
                if commit_code == 0 and commit_count:
                    ahead = int(commit_count)
                else:
                    ahead = 1

        if ahead > 0 and behind > 0:
            sync_state = "DIVERGED"
        elif behind > 0:
            sync_state = "BEHIND"
        elif ahead > 0:
            sync_state = "AHEAD"
        else:
            sync_state = "UP_TO_DATE"

        return GitStatusResult(
            sync_state=sync_state,
            is_dirty=is_dirty,
            current_branch=branch,
            ahead_count=ahead,
            behind_count=behind,
            dirty_files=dirty_files
        )

    def execute_smart_pull(self, repo_path: Path, branch: str, lang: str = "en") -> Tuple[bool, str]:
        l = GIT_LOCALIZED.get(lang, GIT_LOCALIZED["en"])
        remote_name = self.resolve_remote_name(repo_path, branch) or "origin"
        code, out, err = self.run_cmd(["pull", "--ff-only", remote_name, branch], cwd=repo_path)
        if code == 0:
            return True, l["pull_ok"]
        return False, l["pull_ff_err"].format(err)

    def execute_smart_push(self, repo_path: Path, branch: str, lang: str = "en") -> Tuple[bool, str]:
        l = GIT_LOCALIZED.get(lang, GIT_LOCALIZED["en"])
        remote_name = self.resolve_remote_name(repo_path, branch) or "origin"
        code, out, err = self.run_cmd(["push", remote_name, branch], cwd=repo_path)
        if code == 0:
            return True, l["push_ok"]
        return False, l["push_err"].format(err)

    def execute_commit_and_push(self, repo_path: Path, branch: str, lang: str = "en") -> Tuple[bool, str]:
        l = GIT_LOCALIZED.get(lang, GIT_LOCALIZED["en"])
        remote_name = self.resolve_remote_name(repo_path, branch) or "origin"
        self.run_cmd(["add", "."], cwd=repo_path)
        self.run_cmd(["commit", "-m", "auto sync: local updates"], cwd=repo_path)
        code, out, err = self.run_cmd(["push", remote_name, branch], cwd=repo_path)
        if code == 0:
            return True, l["push_ok"]
        return False, l["push_err"].format(err)
