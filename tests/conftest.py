from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.repository.task_repo import TaskRepository
from app.services.todo_service import TodoService
from db.models.task import TaskORM  # noqa: F401 – needed for metadata
from db.base import Base

import asyncio
import pytest
import pytest_asyncio


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Single event loop for the whole test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def engine():
    _engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield _engine
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await _engine.dispose()


@pytest_asyncio.fixture()
async def session(engine) -> AsyncSession:
    factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture()
async def repo(session: AsyncSession) -> TaskRepository:
    return TaskRepository(session)


@pytest_asyncio.fixture()
async def service(engine) -> TodoService:
    factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    return TodoService(factory)