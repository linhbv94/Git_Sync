import asyncio
from pathlib import Path
from typing import List, Tuple, Dict
from src.git_engine import GitEngine, GitStatusResult

class SyncEngine:
    def __init__(self, scan_path: str, ignore_list: List[str], max_depth: int = 3, timeout: int = 10, max_concurrency: int = 8, lang: str = "en"):
        self.scan_path = Path(scan_path).expanduser().resolve()
        self.ignore_list = ignore_list
        self.max_depth = max_depth
        self.timeout = timeout
        self.max_concurrency = max_concurrency
        self.lang = lang
        self.git_engine = GitEngine()

    def scan_workspace(self) -> List[Path]:
        """Scans the workspace recursively for Git repositories."""
        if not self.scan_path.exists() or not self.scan_path.is_dir():
            return []
        return self._recursive_scan(self.scan_path, 1)

    def _recursive_scan(self, current_dir: Path, current_depth: int) -> List[Path]:
        if current_depth > self.max_depth:
            return []
        
        # Check ignore list by directory name
        if current_dir.name in self.ignore_list:
            return []
        
        # Check ignore list by relative path parts
        try:
            rel_path = current_dir.relative_to(self.scan_path)
            if any(part in self.ignore_list for part in rel_path.parts):
                return []
        except ValueError:
            pass

        # If a .git directory is found, stop scanning deeper under this path
        if (current_dir / ".git").is_dir():
            return [current_dir]

        repos = []
        try:
            for child in current_dir.iterdir():
                if child.is_dir():
                    repos.extend(self._recursive_scan(child, current_depth + 1))
        except PermissionError:
            pass  # Skip directories with permission errors
        except Exception:
            pass
        
        return repos

    async def check_all_repos(self, repo_paths: List[Path]) -> List[Tuple[Path, GitStatusResult]]:
        """Concurrently fetches and analyzes git status for all discovered repositories."""
        sem = asyncio.Semaphore(self.max_concurrency)
        tasks = [self._check_repo_task(path, sem) for path in repo_paths]
        return await asyncio.gather(*tasks)

    async def _check_repo_task(self, repo_path: Path, sem: asyncio.Semaphore) -> Tuple[Path, GitStatusResult]:
        async with sem:
            result = await asyncio.to_thread(self.git_engine.get_git_status, repo_path, self.lang, self.timeout)
            return repo_path, result

    async def execute_smart_sync_all(self, repos_status: List[Tuple[Path, GitStatusResult]]) -> List[Tuple[Path, str, bool, str]]:
        """
        Runs smart pull on BEHIND clean repos and smart push on AHEAD clean repos.
        Returns List of (repo_path, action, success, message).
        """
        sem = asyncio.Semaphore(self.max_concurrency)
        tasks = []
        for path, status in repos_status:
            if status.sync_state == "BEHIND" and not status.is_dirty:
                tasks.append(self._pull_task(path, status.current_branch, sem))
            elif status.sync_state == "AHEAD" and not status.is_dirty:
                tasks.append(self._push_task(path, status.current_branch, sem))
        
        if not tasks:
            return []
            
        return await asyncio.gather(*tasks)

    async def execute_smart_pull_only(self, repos_status: List[Tuple[Path, GitStatusResult]]) -> List[Tuple[Path, str, bool, str]]:
        sem = asyncio.Semaphore(self.max_concurrency)
        tasks = []
        for path, status in repos_status:
            if status.sync_state == "BEHIND" and not status.is_dirty:
                tasks.append(self._pull_task(path, status.current_branch, sem))
        
        if not tasks:
            return []
        return await asyncio.gather(*tasks)

    async def execute_smart_push_only(self, repos_status: List[Tuple[Path, GitStatusResult]]) -> List[Tuple[Path, str, bool, str]]:
        sem = asyncio.Semaphore(self.max_concurrency)
        tasks = []
        for path, status in repos_status:
            if status.sync_state == "AHEAD" and not status.is_dirty:
                tasks.append(self._push_task(path, status.current_branch, sem))
        
        if not tasks:
            return []
        return await asyncio.gather(*tasks)

    async def _pull_task(self, repo_path: Path, branch: str, sem: asyncio.Semaphore) -> Tuple[Path, str, bool, str]:
        async with sem:
            success, msg = await asyncio.to_thread(self.git_engine.execute_smart_pull, repo_path, branch, self.lang)
            return repo_path, "PULL", success, msg

    async def _push_task(self, repo_path: Path, branch: str, sem: asyncio.Semaphore) -> Tuple[Path, str, bool, str]:
        async with sem:
            success, msg = await asyncio.to_thread(self.git_engine.execute_smart_push, repo_path, branch, self.lang)
            return repo_path, "PUSH", success, msg
