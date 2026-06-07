# Ajax Todo — тестовый проект (Junior Python Developer in Test)

Десктопное Todo-приложение на **Python + Tkinter** с асинхронным слоем данных
(**SQLAlchemy async + aiomysql**) и полным набором автотестов (**pytest-asyncio**).

## Стек

| Слой | Технология |
|------|-----------|
| UI | Tkinter (stdlib) |
| Бизнес-логика | чистые датаклассы + сервисный слой |
| ORM | SQLAlchemy 2.x async (mapped_column) |
| DB driver | aiomysql |
| БД (прод) | MySQL 8 в Docker |
| БД (тесты) | SQLite in-memory (aiosqlite) |
| Тесты | pytest + pytest-asyncio + pytest-cov |

## Структура проекта

```
to_do_ajax/
├── app/
│   ├── models/task.py          # Доменная модель (dataclass)
│   ├── repository/task_repo.py # Слой доступа к данным
│   ├── services/todo_service.py# Бизнес-логика
│   ├── ui/main_window.py       # Tkinter UI
│   └── main.py                 # Точка входа
├── db/
│   ├── base.py                 # DeclarativeBase
│   ├── session.py              # Engine + AsyncSessionLocal
│   └── models/task.py          # ORM-модель (TaskORM)
├── tests/
│   ├── conftest.py             # Фикстуры (SQLite in-memory)
│   ├── unit/                   # Тесты сервиса и репозитория
│   ├── integration/            # Тесты работы с БД
│   └── e2e/                    # Сквозные пользовательские сценарии
├── scripts/init.sql            # DDL для MySQL
├── report/                     # HTML-отчёт покрытия (генерируется)
├── docker-compose.yml
├── pytest.ini
├── requirements.txt
└── .env
```

## Быстрый старт

### 1. Клонировать и установить зависимости

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# для тестов без MySQL нужен aiosqlite:
pip install aiosqlite
```

### 2. Поднять MySQL в Docker

```bash
docker-compose up -d
# Дождитесь healthcheck (≈10 сек)
docker-compose ps
```

### 3. Запустить приложение

```bash
python -m app.main
```

### 4. Запустить тесты (без Docker — SQLite in-memory)

```bash
pytest
```

HTML-отчёт о покрытии будет в `report/coverage/index.html`.

## Переменные окружения (`.env`)

```
DB_USER=todo_user
DB_PASSWORD=todo_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=todo_db
```

## Архитектурные решения

- **Разделение ORM / домен** — `db/models/task.py` (SQLAlchemy) и `app/models/task.py`
  (чистый dataclass) не зависят друг от друга. Это упрощает тестирование бизнес-логики
  без поднятия БД.
- **AsyncRunner** — фоновый поток с event loop позволяет использовать `async/await`
  в синхронном Tkinter mainloop без блокировки UI.
- **Тесты на SQLite** — вся тестовая инфраструктура не требует MySQL; конфигурация
  движка подменяется в `conftest.py`.
