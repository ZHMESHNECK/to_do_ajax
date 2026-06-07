"""Unit tests for TaskRepository CRUD operations."""

import pytest
from app.models.task import Task
from app.repository.task_repo import TaskRepository


@pytest.mark.asyncio
class TestTaskRepository:
    async def test_create_and_get_by_id(self, repo: TaskRepository):
        task = await repo.create(Task(title="Repo task"))
        fetched = await repo.get_by_id(task.row_id)
        assert fetched is not None
        assert fetched.title == "Repo task"

    async def test_get_by_id_missing_returns_none(self, repo: TaskRepository):
        result = await repo.get_by_id(999999)
        assert result is None

    async def test_get_all_returns_created(self, repo: TaskRepository):
        await repo.create(Task(title="Alpha"))
        await repo.create(Task(title="Beta"))
        all_tasks = await repo.get_all()
        titles = {t.title for t in all_tasks}
        assert {"Alpha", "Beta"}.issubset(titles)

    async def test_get_all_search_filters(self, repo: TaskRepository):
        await repo.create(Task(title="Search me"))
        await repo.create(Task(title="Ignore me"))
        results = await repo.get_all(search="Search")
        assert all("search" in t.title.lower() for t in results)

    async def test_update_changes_fields(self, repo: TaskRepository):
        task = await repo.create(Task(title="Original"))
        task.update(title="Updated", description="new desc")
        updated = await repo.update(task)
        assert updated.title == "Updated"
        assert updated.description == "new desc"

    async def test_update_nonexistent_raises(self, repo: TaskRepository):
        with pytest.raises(ValueError):
            await repo.update(Task(row_id=999999, title="Ghost"))

    async def test_delete_removes_record(self, repo: TaskRepository):
        task = await repo.create(Task(title="To delete"))
        await repo.delete(task.row_id)
        assert await repo.get_by_id(task.row_id) is None
