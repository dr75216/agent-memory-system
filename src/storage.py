"""Storage layer for the Agent Memory System."""

import json
from pathlib import Path

from .issue import Issue


class StorageError(Exception):
    """Base exception for storage-related errors."""
    pass


class IssueStore:
    """Handles persistence of issues to .ams directory."""

    AMS_DIR = ".ams"
    ISSUES_FILE = "issues.jsonl"
    META_FILE = "meta.json"
    VERSION = "1.0"

    def __init__(self, base_path: str = ".") -> None:
        """
        Initialize the store with a base path.

        Args:
            base_path: Directory where .ams folder will be created.
        """
        self.base_path = Path(base_path)
        self.ams_path = self.base_path / self.AMS_DIR
        self.issues_path = self.ams_path / self.ISSUES_FILE
        self.meta_path = self.ams_path / self.META_FILE

    def init(self) -> None:
        """
        Initialize the .ams directory structure.

        Creates .ams/, issues.jsonl, and meta.json if they don't exist.
        """
        self.ams_path.mkdir(parents=True, exist_ok=True)

        if not self.issues_path.exists():
            self.issues_path.touch()

        if not self.meta_path.exists():
            self._write_meta({"next_id": 1, "version": self.VERSION})

    def _ensure_initialized(self) -> None:
        """Auto-initialize if .ams doesn't exist."""
        if not self.ams_path.exists():
            self.init()

    def _read_meta(self) -> dict:
        """Read meta.json and return its contents."""
        self._ensure_initialized()
        try:
            with open(self.meta_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise StorageError(f"Corrupted meta.json: {e}")

    def _write_meta(self, data: dict) -> None:
        """Write data to meta.json."""
        with open(self.meta_path, "w") as f:
            json.dump(data, f, indent=2)

    def get_next_id(self) -> int:
        """
        Get the next available issue ID and increment the counter.

        Returns:
            The next available ID.
        """
        meta = self._read_meta()
        next_id = meta["next_id"]
        meta["next_id"] = next_id + 1
        self._write_meta(meta)
        return next_id

    def load_all(self) -> list[Issue]:
        """
        Load all issues from the JSONL file.

        Returns:
            List of Issue objects.

        Raises:
            StorageError: If JSONL contains invalid data.
        """
        self._ensure_initialized()
        issues: list[Issue] = []

        if not self.issues_path.exists() or self.issues_path.stat().st_size == 0:
            return issues

        with open(self.issues_path, "r") as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    issue = Issue.from_dict(data)
                    issues.append(issue)
                except json.JSONDecodeError as e:
                    raise StorageError(
                        f"Corrupted JSONL at line {line_num}: {e}"
                    )
                except (KeyError, ValueError) as e:
                    raise StorageError(
                        f"Invalid issue data at line {line_num}: {e}"
                    )

        return issues

    def _write_all(self, issues: list[Issue]) -> None:
        """Write all issues to the JSONL file (overwrites)."""
        with open(self.issues_path, "w") as f:
            for issue in issues:
                f.write(json.dumps(issue.to_dict()) + "\n")

    def save_issue(self, issue: Issue) -> None:
        """
        Save an issue to the store.

        If the issue ID exists, updates it. Otherwise, appends it.

        Args:
            issue: The Issue to save.
        """
        self._ensure_initialized()
        issues = self.load_all()

        # Check if issue exists (update) or is new (append)
        existing_idx = None
        for idx, existing in enumerate(issues):
            if existing.id == issue.id:
                existing_idx = idx
                break

        if existing_idx is not None:
            issues[existing_idx] = issue
        else:
            issues.append(issue)

        self._write_all(issues)

    def get_by_id(self, id: int) -> Issue | None:
        """
        Get an issue by its ID.

        Args:
            id: The issue ID to find.

        Returns:
            The Issue if found, None otherwise.
        """
        issues = self.load_all()
        for issue in issues:
            if issue.id == id:
                return issue
        return None

    def get_all_ids(self) -> set[int]:
        """
        Get all existing issue IDs.

        Returns:
            Set of all issue IDs in the store.
        """
        issues = self.load_all()
        return {issue.id for issue in issues}
