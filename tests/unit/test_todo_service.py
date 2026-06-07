"""Unit tests for TodoService business logic."""

import pytest
from app.services.todo_service import TodoService


@pytest.mark.asyncio
class TestCreateTask:
    async def test_create_returns_task_with_id(self, service: TodoService):
        task = await service.create_task("Buy milk")
        assert task.row_id is not None
        assert task.title == "Buy milk"
        assert task.is_done is False

    async def test_create_strips_whitespace(self, service: TodoService):
        task = await service.create_task("  Hello  ", "  desc  ")
        assert task.title == "Hello"
        assert task.description == "desc"

    async def test_create_empty_title_raises(self, service: TodoService):
        with pytest.raises(ValueError, match="empty"):
            await service.create_task("   ")

    async def test_create_title_too_long_raises(self, service: TodoService):
        with pytest.raises(ValueError, match="255"):
            await service.create_task("x" * 256)


@pytest.mark.asyncio
class TestListTasks:
    async def test_list_returns_all(self, service: TodoService):
        await service.create_task("Task A")
        await service.create_task("Task B")
        tasks = await service.list_tasks()
        titles = {t.title for t in tasks}
        assert {"Task A", "Task B"}.issubset(titles)

    async def test_search_filters_by_title(self, service: TodoService):
        await service.create_task("Buy groceries")
        await service.create_task("Read book")
        results = await service.list_tasks(search="groceries")
        assert all("groceries" in t.title.lower() for t in results)


@pytest.mark.asyncio
class TestToggleTask:
    async def test_toggle_marks_done(self, service: TodoService):
        task = await service.create_task("Do laundry")
        toggled = await service.toggle_task(task.row_id)
        assert toggled.is_done is True

    async def test_toggle_twice_restores(self, service: TodoService):
        task = await service.create_task("Double toggle")
        await service.toggle_task(task.row_id)
        restored = await service.toggle_task(task.row_id)
        assert restored.is_done is False

    async def test_toggle_nonexistent_raises(self, service: TodoService):
        with pytest.raises(ValueError, match="not found"):
            await service.toggle_task(999999)


@pytest.mark.asyncio
class TestUpdateTask:
    async def test_update_title_and_description(self, service: TodoService):
        task = await service.create_task("Old title")
        updated = await service.update_task(task.row_id, "New title", "new desc")
        assert updated.title == "New title"
        assert updated.description == "new desc"

    async def test_update_empty_title_raises(self, service: TodoService):
        task = await service.create_task("Valid title")
        with pytest.raises(ValueError):
            await service.update_task(task.row_id, "")


@pytest.mark.asyncio
class TestDeleteTask:
    async def test_delete_removes_task(self, service: TodoService):
        task = await service.create_task("Temporary task")
        await service.delete_task(task.row_id)
        tasks = await service.list_tasks()
        assert all(t.row_id != task.row_id for t in tasks)

    async def test_delete_nonexistent_raises(self, service: TodoService):
        with pytest.raises(ValueError, match="not found"):
            await service.delete_task(999999)
