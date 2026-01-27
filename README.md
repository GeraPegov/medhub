# MedHub

**MedHub** — server-side web‑приложение на **FastAPI** для публикации статей (в т.ч. медицинской тематики): лента, поиск, профили авторов, подписки, комментарии и реакции **like/dislike**.

## Возможности

- **Аутентификация**: регистрация/логин, JWT‑токен в **HttpOnly cookie** `access_token`, выход из аккаунта.
- **Статьи**:
  - публикация/редактирование/удаление;
  - поиск по **заголовку** и фильтрация по **категории**;
  - **лимит публикаций**: до **3 статей в день** на пользователя.
- **Реакции**: like/dislike на статью, **не чаще 1 раза в день** для пары `(user_id, article_id)`.
- **Комментарии**: добавление/удаление комментариев к статье, отображение в профиле.
- **Профиль пользователя**: список статей, комментариев, подписок, лайкнутых статей; “удаление профиля” (soft delete через `is_deleted`).
- **Кеширование**: Redis‑кеш для пользователей/статей (TTL по умолчанию 1 час).

## Технологии

- **Python** 3.11
- **FastAPI**, **Uvicorn**
- **PostgreSQL**, **SQLAlchemy (async)** + **asyncpg**
- **Alembic** (миграции)
- **Redis** (async client)
- **Jinja2** (HTML‑шаблоны + статика)
- **JWT** (`python-jose`), хеширование пароля (`passlib[bcrypt]`, `argon2_cffi`)
- **Pytest** (`pytest-asyncio`, `httpx`) + Ruff (линтер/форматирование)

## Архитектура

Проект разложен по слоям (DDD-подобная структура):

- `app/presentation` — роуты FastAPI, шаблоны/статика, DI‑зависимости
- `app/application` — сервисы и DTO, бизнес‑сценарии
- `app/domain` — сущности и интерфейсы репозиториев/сервисов
- `app/infrastructure` — конфиг, БД, реализации репозиториев, интеграции

Точка входа: `main.py` (FastAPI app + lifespan для Redis).

## Роуты (основные)

- **Лента**: `GET /`
- **Регистрация**: `GET /register`, `POST /auth/register`
- **Логин**: `GET /auth`, `POST /auth/login`
- **Выход**: `GET /exit`
- **Статья**:
  - `GET /article/submit`, `POST /article/submit/add`
  - `GET /article/{article_id}`
  - `GET /article/change/{article_id}`, `POST /article/change/{article_id}/access`
  - `POST /article/delete/{article_id}`
  - `POST /article/{reaction}/{article_id}` (reaction = `like|dislike`)
- **Поиск**: `GET /articles/search`, `GET /articles/search/title`, `GET /articles/search/category/{category}`
- **Комментарии**: `POST /comments/{article_id}/create`, `POST /comments/{comment_id}/delete`
- **Профиль**: `GET /user/profile/{unique_username}` + разделы `/articles`, `/comments`, `/subscriptions`, `/liked`, подписка/отписка, удаление профиля.

## Запуск локально

### 1 Требования

- Python **3.11**
- PostgreSQL
- Redis

### 2 Установка зависимостей

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 3 Переменные окружения

Скопируйте пример и заполните значения:

```bash
cp env.example .env
```

### 4 Создание БД и миграции

Вариант A: создать базы автоматически (нужен доступ к `ADMIN_DB_URL`):

```bash
python -m scripts.init_db
```

Вариант B: создать базы вручную и просто накатить миграции.

Миграции Alembic:

```bash
alembic upgrade head
```

### 5 Запуск приложения

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Откройте в браузере: `http://localhost:8000`.

## Тесты

Тесты используют `TEST_DB_URL` и Redis из `.env`:

```bash
pytest
```

## Примечания по бизнес-правилам

- **Публикации**: максимум **3 статьи в день** на пользователя (проверка на уровне `LogicRepository.check_limited`).
- **Реакции**: ограничение “1 реакция в день” реализовано через запись даты реакции в Redis‑ключе вида `user{user_id}:article{article_id}`.

## Текст для резюме (готовый блок)

**MedHub** — медицинский контент‑хаб (server-side web‑приложение) на **FastAPI**: лента статей, поиск, профили авторов, подписки, комментарии и реакции.  
Стек: **Python 3.11**, FastAPI, PostgreSQL, SQLAlchemy (async) + asyncpg, Redis, Alembic, JWT, Jinja2, Pytest.

Что сделал(а):

- Спроектировал(а) DDD‑подобную структуру (слои `presentation/application/domain/infrastructure`) и DI‑зависимости FastAPI.
- Реализовал(а) регистрацию/логин/выход и JWT‑аутентификацию с хранением токена в **HttpOnly cookie**.
- Реализовал(а) CRUD статей + поиск по заголовку/категории и отображение ленты.
- Внедрил(а) бизнес‑ограничения: **до 3 публикаций в день** и **реакции like/dislike не чаще 1 раза в день**.
- Интегрировал(а) Redis‑кеширование пользователей/статей (TTL 1 час) для ускорения отображения страниц.
- Настроил(а) слой данных на PostgreSQL + SQLAlchemy async и миграции Alembic.
- Написал(а) асинхронные тесты (pytest‑asyncio) для репозиториев/сервисов с изоляцией тестовой БД.

