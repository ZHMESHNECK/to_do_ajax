from app.services.todo_service import TodoService
import pytest


@pytest.mark.asyncio
class TestUserWorkflows:
    async def test_user_creates_and_sees_task(self, service: TodoService):
        """A user creates a task and it appears in the list."""
        await service.create_task("Buy coffee", "Single origin")
        tasks = await service.list_tasks()
        assert any(t.title == "Buy coffee" for t in tasks)

    async def test_user_edits_task(self, service: TodoService):
        """A user edits a task title and sees the change."""
        task = await service.create_task("Old name")
        await service.update_task(task.row_id, "New name")
        tasks = await service.list_tasks()
        assert any(t.title == "New name" for t in tasks)
        assert all(t.title != "Old name" for t in tasks)

    async def test_user_completes_task(self, service: TodoService):
        """A user marks a task as done."""
        task = await service.create_task("Finish report")
        await service.toggle_task(task.row_id)
        tasks = await service.list_tasks()
        updated = next(t for t in tasks if t.row_id == task.row_id)
        assert updated.is_done is True

    async def test_user_deletes_task(self, service: TodoService):
        """A user deletes a task and it disappears."""
        task = await service.create_task("Temp task")
        await service.delete_task(task.row_id)
        tasks = await service.list_tasks()
        assert all(t.row_id != task.row_id for t in tasks)

    async def test_user_searches_tasks(self, service: TodoService):
        """A user searches by keyword and sees only relevant tasks."""
        await service.create_task("Morning run")
        await service.create_task("Evening swim")
        results = await service.list_tasks(search="morning")
        assert len(results) >= 1
        assert all("morning" in t.title.lower() for t in results)

    async def test_full_lifecycle(self, service: TodoService):
        """Create → search → edit → complete → delete."""
        task = await service.create_task("Lifecycle task")

        # search finds it
        found = await service.list_tasks(search="Lifecycle")
        assert any(t.row_id == task.row_id for t in found)

        # edit it
        await service.update_task(task.row_id, "Lifecycle task (edited)")

        # complete it
        done = await service.toggle_task(task.row_id)
        assert done.is_done is True

        # delete it
        await service.delete_task(task.row_id)
        all_tasks = await service.list_tasks()
        assert all(t.row_id != task.row_id for t in all_tasks)
