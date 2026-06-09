from app.repository.task_repo import TaskRepository
from app.services.todo_service import TodoService
from app.ui.main_window import AsyncRunner, MainWindow
from db.session import engine, AsyncSessionLocal
from db.base import Base
import asyncio
import tkinter as tk


async def init_db() -> None:
    """Create tables if they don't exist (useful for dev without Docker)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def main():
    asyncio.run(init_db())

    root = tk.Tk()

    runner = AsyncRunner()
    service = TodoService(AsyncSessionLocal)

    app = MainWindow(root, service, runner)

    def on_close():
        runner.stop()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)

    root.mainloop()


if __name__ == "__main__":
    main() 
