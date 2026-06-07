from sqlalchemy import text
from app.repository.task_repo import TaskRepository
from app.models.task import Task
import pytest


@pytest.mark.asyncio
class TestDatabaseIntegration:
    async def test_tables_exist(self, session):
        """Ensure the tasks table was created by fixture."""
        result = await session.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        table_names = {row[0] for row in result.fetchall()}
        assert "tasks" in table_names

    async def test_create_persists(self, repo: TaskRepository):
        task = await repo.create(Task(title="Persisted task", description="db test"))
        assert task.row_id is not None
        fetched = await repo.get_by_id(task.row_id)
        assert fetched.title == "Persisted task"
        assert fetched.description == "db test"

    async def test_update_persists(self, repo: TaskRepository):
        task = await repo.create(Task(title="Before update"))
        task.update("After update", "changed")
        updated = await repo.update(task)
        fetched = await repo.get_by_id(updated.row_id)
        assert fetched.title == "After update"

    async def test_delete_persists(self, repo: TaskRepository):
        task = await repo.create(Task(title="Will be deleted"))
        await repo.delete(task.row_id)
        fetched = await repo.get_by_id(task.row_id)
        assert fetched is None

    async def test_is_done_default_false(self, repo: TaskRepository):
        task = await repo.create(Task(title="New task"))
        assert task.is_done is False

    async def test_toggle_is_done(self, repo: TaskRepository):
        task = await repo.create(Task(title="Toggle me"))
        task.mark_done()
        updated = await repo.update(task)
        assert updated.is_done is True
