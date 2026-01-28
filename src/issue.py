"""Issue data class for the Agent Memory System."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class Status(Enum):
    """Issue status values."""
    OPEN = "open"
    IN_PROGRESS = "in-progress"
    DONE = "done"


@dataclass
class Issue:
    """Represents a single issue in the memory system."""

    id: int
    title: str
    description: str | None
    status: Status
    created_at: datetime
    updated_at: datetime
    blocked_by: list[int] = field(default_factory=list)

    def validate_blocked_by(self, existing_ids: set[int]) -> None:
        """
        Validate that all blocked_by IDs reference existing issues.

        Args:
            existing_ids: Set of all valid issue IDs in the system.

        Raises:
            ValueError: If any blocked_by ID doesn't exist.
        """
        invalid_ids = set(self.blocked_by) - existing_ids
        if invalid_ids:
            raise ValueError(
                f"Invalid blocked_by IDs: {sorted(invalid_ids)}. "
                f"These issues do not exist."
            )

        # Can't block yourself
        if self.id in self.blocked_by:
            raise ValueError(f"Issue {self.id} cannot block itself.")

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize issue to a dictionary (for JSON storage).

        Returns:
            Dictionary representation of the issue.
        """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "blocked_by": self.blocked_by,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Issue":
        """
        Deserialize issue from a dictionary (from JSON storage).

        Args:
            data: Dictionary with issue fields.

        Returns:
            Issue instance.

        Raises:
            KeyError: If required fields are missing.
            ValueError: If field values are invalid.
        """
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description"),
            status=Status(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            blocked_by=data.get("blocked_by", []),
        )

    @classmethod
    def create(
        cls,
        id: int,
        title: str,
        description: str | None = None,
        blocked_by: list[int] | None = None,
    ) -> "Issue":
        """
        Factory method to create a new issue with auto-set timestamps.

        Args:
            id: Unique issue ID.
            title: Issue title.
            description: Optional description.
            blocked_by: List of issue IDs that block this one.

        Returns:
            New Issue instance with current timestamp.
        """
        now = datetime.now(timezone.utc)
        return cls(
            id=id,
            title=title,
            description=description,
            status=Status.OPEN,
            created_at=now,
            updated_at=now,
            blocked_by=blocked_by or [],
        )
