import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

load_dotenv()

_user = os.getenv("DB_USER", "todo_user")
_password = os.getenv("DB_PASSWORD", "todo_password")
_host = os.getenv("DB_HOST", "localhost")
_port = os.getenv("DB_PORT", "3306")
_name = os.getenv("DB_NAME", "todo_db")

DATABASE_URL = f"mysql+aiomysql://{_user}:{_password}@{_host}:{_port}/{_name}"

engine = create_async_engine(
    DATABASE_URL, 
    echo=False,
    poolclass=NullPool
)

AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
