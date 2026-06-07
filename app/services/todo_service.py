from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from app.repository.task_repo import TaskRepository
from app.models.task import Task


class TodoService:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession],
                 ) -> None:
        self._session_factory = session_factory

    async def list_tasks(self, search: str = ""):
        async with self._session_factory() as session:
            repo = TaskRepository(session)
            return await repo.get_all(search=search.strip())

    async def create_task(self, title: str, description: str = ""):
        title = title.strip()
        if not title:
            raise ValueError("Task title must not be empty.")
        if len(title) > 255:
            raise ValueError("Task title must be 255 characters or fewer.")

        async with self._session_factory() as session:
            repo = TaskRepository(session)
            task = Task(title=title, description=description.strip())
            return await repo.create(task)

    async def update_task(
        self, task_id: int, title: str, description: str = ""
    ):
        title = title.strip()
        if not title:
            raise ValueError("Task title must not be empty.")
        async with self._session_factory() as session:
            repo = TaskRepository(session)
            task = await repo.get_by_id(task_id)
            if task is None:
                raise ValueError(f"Task {task_id} not found.")
            task.update(title=title, description=description.strip())
            return await repo.update(task)

    async def toggle_task(self, task_id: int):
        async with self._session_factory() as session:
            repo = TaskRepository(session)
            task = await repo.get_by_id(task_id)
            if task is None:
                raise ValueError(f"Task {task_id} not found.")
            task.mark_undone() if task.is_done else task.mark_done()
            return await repo.update(task)

    async def delete_task(self, task_id: int) -> None:
        async with self._session_factory() as session:
            repo = TaskRepository(session)
            task = await repo.get_by_id(task_id)
            if task is None:
                raise ValueError(f"Task {task_id} not found.")
            await repo.delete(task_id)
