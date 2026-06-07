from datetime import datetime, timezone

import pytz
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from db.models.task import TaskORM


def _orm_to_domain(orm: TaskORM) -> Task:
    return Task(
        row_id=orm.row_id,
        title=orm.title,
        description=orm.description or "",
        is_done=orm.is_done,
        created_at=orm.created_at.replace(tzinfo=timezone.utc),
        updated_at=orm.updated_at.replace(tzinfo=timezone.utc),
    )


class TaskRepository:
    def __init__(self, session: AsyncSession,
    ) -> None:
        self._session = session

    async def get_all(self, search: str = "") -> list[Task]:
        stmt = select(TaskORM).order_by(TaskORM.created_at.desc())
        if search:
            stmt = stmt.where(TaskORM.title.ilike(f"%{search}%"))
        result = await self._session.execute(stmt)
        return [_orm_to_domain(row) for row in result.scalars().all()]

    async def get_by_id(self, task_id: int) -> Task | None:
        result = await self._session.get(TaskORM, task_id)
        return _orm_to_domain(result) if result else None

    async def create(self, task: Task) -> Task:
        orm = TaskORM(
            title=task.title,
            description=task.description,
            is_done=task.is_done,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        self._session.add(orm)
        await self._session.commit()
        await self._session.refresh(orm)
        return _orm_to_domain(orm)

    async def update(self, task: Task) -> Task:
        orm = await self._session.get(TaskORM, task.row_id)
        if orm is None:
            raise ValueError(f"Task with id={task.row_id} not found")
        orm.title = task.title
        orm.description = task.description
        orm.is_done = task.is_done
        orm.updated_at = datetime.now(timezone.utc)
        await self._session.commit()
        await self._session.refresh(orm)
        return _orm_to_domain(orm)

    async def delete(self, task_id: int) -> None:
        await self._session.execute(delete(TaskORM).where(TaskORM.row_id == task_id))
        await self._session.commit()
