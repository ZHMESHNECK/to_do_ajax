from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Task:
    """Pure domain model — no SQLAlchemy dependency."""

    title: str
    description: str = ""
    is_done: bool = False
    row_id: int | None = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def mark_done(self) -> None:
        self.is_done = True
        self.updated_at = datetime.now()

    def mark_undone(self) -> None:
        self.is_done = False
        self.updated_at = datetime.now()

    def update(self, title: str, description: str = "") -> None:
        self.title = title
        self.description = description
        self.updated_at = datetime.now()
