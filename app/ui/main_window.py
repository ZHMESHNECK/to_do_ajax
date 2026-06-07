from tkinter import messagebox, simpledialog, ttk
from typing import Callable
from app.models.task import Task
from app.services.todo_service import TodoService
import threading
import asyncio
import tkinter as tk
import config


class AsyncRunner:
    """Runs coroutines on a dedicated thread's event loop."""

    def __init__(self) -> None:
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(
            target=self._run_loop, daemon=True
        )
        self._thread.start()
        self._stopping = False

    def _run_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def run(self, coro, callback: Callable | None = None) -> None:
        if self._stopping or not self._loop.is_running():
            if callback:
                callback(RuntimeError("Event loop is not running"))
            return
            
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)

        if callback:
            def _done(f):
                if self._stopping:
                    return
                try:
                    result = f.result()
                except Exception as e:
                    result = e
                try:
                    callback(result)
                except Exception:
                    pass

            future.add_done_callback(_done)

    def stop(self):
        """Safe shutdown of event loop."""
        if self._stopping:
            return
            
        self._stopping = True

        async def shutdown():
            from db.session import engine
            tasks = [t for t in asyncio.all_tasks(self._loop) if t is not asyncio.current_task()]
            for t in tasks:
                t.cancel()
                try:
                    await t
                except asyncio.CancelledError:
                    pass
            
            # Dispose engine to close all database connections
            await engine.dispose()

        fut = asyncio.run_coroutine_threadsafe(shutdown(), self._loop)
        try:
            fut.result(timeout=3)
        except Exception:
            pass

        self._loop.call_soon_threadsafe(self._loop.stop)

        self._thread.join(timeout=3)


class MainWindow:
    def __init__(self, root: tk.Tk, service: TodoService, runner: AsyncRunner) -> None:
        self._root = root
        self._service = service
        self._runner = runner
        self._tasks: list[Task] = []

        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        self._root.title("Ajax Todo")
        self._root.geometry("720x540")
        self._root.configure(bg=config.BG)
        self._root.resizable(True, True)

        # ── Header ──────────────────────────────────────────────────────── #
        header = tk.Frame(self._root, bg=config.ACCENT, pady=10)
        header.pack(fill="x")
        tk.Label(
            header, text="⚡ Ajax Todo", font=("Segoe UI", 16, "bold"),
            bg=config.ACCENT, fg="white"
        ).pack()

        # ── Search bar ──────────────────────────────────────────────────── #
        search_frame = tk.Frame(self._root, bg=config.BG, pady=6, padx=12)
        search_frame.pack(fill="x")

        tk.Label(search_frame, text="🔍", bg=config.BG,
                 font=("Segoe UI", 12)).pack(side="left")
        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", lambda *_: self.refresh())
        search_entry = tk.Entry(
            search_frame, textvariable=self._search_var,
            font=config.FONT_TITLE, relief="flat", bg="white", fg="#333",
            insertbackground=config.ACCENT
        )
        search_entry.pack(side="left", fill="x", expand=True, ipady=4, padx=6)

        # ── Task list ───────────────────────────────────────────────────── #
        list_frame = tk.Frame(self._root, bg=config.BG, padx=12)
        list_frame.pack(fill="both", expand=True)

        columns = ("done", "title", "description", "created")
        self._tree = ttk.Treeview(
            list_frame, columns=columns, show="headings",
            selectmode="browse", height=16
        )
        self._tree.heading("done",        text="✓",           anchor="center")
        self._tree.heading("title",       text="Title",        anchor="w")
        self._tree.heading("description", text="Description",  anchor="w")
        self._tree.heading("created",     text="Created",      anchor="center")

        self._tree.column("done",        width=36,
                          anchor="center", stretch=False)
        self._tree.column("title",       width=220, anchor="w")
        self._tree.column("description", width=260, anchor="w")
        self._tree.column("created",     width=140,
                          anchor="center", stretch=False)

        style = ttk.Style()
        style.configure("Treeview", font=config.FONT_TITLE,
                        rowheight=28, background="white")
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.map("Treeview", background=[("selected", config.ACCENT)])

        scrollbar = ttk.Scrollbar(
            list_frame, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)

        self._tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._tree.tag_configure("done_tag", foreground=config.DONE_FG)
        self._tree.bind("<Double-1>", lambda _: self._on_toggle())

        # ── Buttons ─────────────────────────────────────────────────────── #
        btn_frame = tk.Frame(self._root, bg=config.BG, pady=8, padx=12)
        btn_frame.pack(fill="x")

        def btn(parent, text, color, cmd):
            return tk.Button(
                parent, text=text, command=cmd,
                bg=color, fg="white", activebackground=color,
                font=("Segoe UI", 10, "bold"), relief="flat",
                padx=14, pady=6, cursor="hand2", bd=0
            )

        btn(btn_frame, "＋  New task",  config.ACCENT,
            self._on_create).pack(side="left", padx=4)
        btn(btn_frame, "✎  Edit",       "#2980b9",
            self._on_edit).pack(side="left", padx=4)
        btn(btn_frame, "✓  Toggle",     config.SUCCESS,
            self._on_toggle).pack(side="left", padx=4)
        btn(btn_frame, "✕  Delete",     config.DANGER,
            self._on_delete).pack(side="left", padx=4)

        # Status bar
        self._status_var = tk.StringVar(value="Ready")
        tk.Label(
            self._root, textvariable=self._status_var,
            bg="#dce1f0", fg="#555", font=("Segoe UI", 9),
            anchor="w", padx=8
        ).pack(fill="x", side="bottom")

        self._root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ---------------------------------------------------------------------- #
    # Data helpers                                                            #
    # ---------------------------------------------------------------------- #

    def _status(self, msg: str) -> None:
        self._status_var.set(msg)

    def _selected_task(self) -> Task | None:
        sel = self._tree.selection()
        if not sel:
            return None
        iid = sel[0]
        idx = self._tree.index(iid)
        return self._tasks[idx] if idx < len(self._tasks) else None

    def _populate(self, tasks: list[Task]) -> None:
        self._tasks = tasks
        for iid in self._tree.get_children():
            self._tree.delete(iid)
        for task in tasks:
            mark = "✓" if task.is_done else ""
            desc = (
                task.description[:40] + "…") if len(task.description) > 40 else task.description
            print(task.created_at)
            created = task.created_at.astimezone().strftime("%Y-%m-%d %H:%M")
            tags = ("done_tag",) if task.is_done else ()
            self._tree.insert("", "end", values=(
                mark, task.title, desc, created), tags=tags)
        total = len(tasks)
        done = sum(1 for t in tasks if t.is_done)
        self._status(f"{total} task(s) — {done} done, {total - done} pending")

    # ---------------------------------------------------------------------- #
    # Actions (bridge sync UI → async service)                               #
    # ---------------------------------------------------------------------- #

    def refresh(self, *_) -> None:
        search = self._search_var.get()

        def callback(result):
            if not self._root.winfo_exists():
                return
            if isinstance(result, Exception):
                self._root.after(0, lambda: messagebox.showerror(
                    "DB Error", str(result)))
                return
            self._root.after(0, lambda: self._populate(result))

        self._runner.run(self._service.list_tasks(search), callback)

    def _on_create(self) -> None:
        title = simpledialog.askstring(
            "New Task", "Task title:", parent=self._root)
        if not title:
            return
        desc = simpledialog.askstring(
            "New Task", "Description (optional):", parent=self._root) or ""

        def callback(result):
            if not self._root.winfo_exists():
                return
            if isinstance(result, Exception):
                self._root.after(
                    0, lambda: messagebox.showerror("Error", str(result)))
            else:
                self._root.after(0, self.refresh)

        self._runner.run(self._service.create_task(title, desc), callback)

    def _on_edit(self) -> None:
        task = self._selected_task()
        if task is None:
            messagebox.showinfo("Select task", "Please select a task to edit.")
            return
        new_title = simpledialog.askstring(
            "Edit Task", "New title:", initialvalue=task.title, parent=self._root
        )
        if not new_title:
            return
        new_desc = simpledialog.askstring(
            "Edit Task", "New description:", initialvalue=task.description, parent=self._root
        ) or ""

        def callback(result):
            if not self._root.winfo_exists():
                return
            if isinstance(result, Exception):
                self._root.after(
                    0, lambda: messagebox.showerror("Error", str(result)))
            else:
                self._root.after(0, self.refresh)

        self._runner.run(self._service.update_task(
            task.row_id, new_title, new_desc), callback)

    def _on_toggle(self) -> None:
        task = self._selected_task()
        if task is None:
            return

        def callback(result):
            if not self._root.winfo_exists():
                return
            if isinstance(result, Exception):
                self._root.after(
                    0, lambda: messagebox.showerror("Error", str(result)))
            else:
                self._root.after(0, self.refresh)

        self._runner.run(self._service.toggle_task(task.row_id), callback)

    def _on_delete(self) -> None:
        task = self._selected_task()
        if task is None:
            messagebox.showinfo(
                "Select task", "Please select a task to delete.")
            return
        if not messagebox.askyesno("Delete", f"Delete «{task.title}»?"):
            return

        def callback(result):
            if not self._root.winfo_exists():
                return
            if isinstance(result, Exception):
                self._root.after(
                    0, lambda: messagebox.showerror("Error", str(result)))
            else:
                self._root.after(0, self.refresh)

        self._runner.run(self._service.delete_task(task.row_id), callback)

    def _on_close(self) -> None:
        self._runner.stop()
        self._root.destroy()
