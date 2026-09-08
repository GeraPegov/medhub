# MedHub — Python-приложение

Пользовательская часть [MedHub](../README.md): лента статей, публикации, профили, подписки, комментарии и реакции. FastAPI обслуживает HTTP-маршруты, Jinja2 — HTML-страницы. Административный интерфейс запрашивает данные у отдельного [Go-сервиса](../admin-services/README.md).

Описание всей системы, бизнес-правил и запуска контейнеров находится в [главном README](../README.md).

## Стек

Python 3.11+, FastAPI, SQLAlchemy Async, asyncpg, PostgreSQL, Redis, Alembic, Pydantic, Jinja2, Uvicorn, APScheduler, pytest и Ruff. В Docker используется Python 3.13.

Пользовательские пароли хешируются Argon2. JWT хранится в HttpOnly cookie `access_token`. Сессия `medhub_session` используется в том числе для CSRF-токенов; её подпись требует `itsdangerous` и отдельного `SECRET_KEY_MIDDLEWARE`.

## Структура

| Каталог | Ответственность |
| --- | --- |
| `app/presentation` | HTTP-обработчики, HTML/CSS/JS, зависимости FastAPI |
| `app/application` | Прикладные сервисы, DTO и аутентификация |
| `app/domain` | Сущности, интерфейсы и исключения |
| `app/infrastructure` | Конфигурация, SQLAlchemy-модели, PostgreSQL- и Redis-репозитории |
| `alembic` | Миграции общей для Python и Go базы |
| `tests` | Тесты сервисов, репозиториев и HTTP-обработчиков |

Точка входа — `main.py`. В `lifespan` создаётся Redis connection pool и запускается APScheduler; при остановке ресурсы закрываются.

## Локальная разработка

### 1. Установить зависимости

Команды ниже выполняются из `fastapi-app`. Понадобятся Python 3.11+ и доступные PostgreSQL и Redis.

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e ".[dev]"
```

Linux / macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e ".[dev]"
```

`requirements.txt` фиксирует версии окружения, а установка `-e ".[dev]"` подключает проект для разработки. Виртуальное окружение создаётся заново на каждой машине.

### 2. Настроить окружение

Если `.env` ещё не создан, скопируйте `.env.example`: `Copy-Item .env.example .env` в PowerShell или `cp .env.example .env` в Linux / macOS. В существующем файле обновите необходимые значения.

| Переменная | Назначение |
| --- | --- |
| `SECRET_KEY` | Секрет подписи пользовательского JWT |
| `SECRET_KEY_MIDDLEWARE` | Отдельный секрет подписи сессионной cookie |
| `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES` | Алгоритм JWT и срок действия в минутах |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | Параметры PostgreSQL; используются также в Compose |
| `ADMIN_DB_URL` | Подключение с правом создания БД |
| `PROD_DB_URL` | Подключение к базе приложения `medhub` |
| `TEST_DB_URL` | Подключение к отдельной тестовой базе `testmedhub` |
| `HOST_REDIS`, `PORT_REDIS` | Адрес Redis |
| `ADMIN_API_URL` | Адрес Go API; локально `http://127.0.0.1:8001` |

Все перечисленные поля обязательны в [Settings](app/infrastructure/config.py). Python-строки подключения используют `postgresql+asyncpg://`. При изменении пароля PostgreSQL обновите его и в строках подключения.

### 3. Подготовить БД и применить миграции

Если PostgreSQL и Redis запускаются через Compose, из `fastapi-app`:

```bash
docker compose up -d db redis
```

При первом запуске нового тома `init.sql` создаёт `medhub`. Для самостоятельно установленного PostgreSQL создайте эту базу заранее, например клиентской командой `createdb -h localhost -U postgres medhub` (замените пользователя на свой).

Затем примените миграции из активированного Python-окружения:

```bash
alembic upgrade head
```

Миграции создают в том числе таблицу администраторов для Go-сервиса. Старый `python -m scripts.init_db` пока не используется в этой инструкции: в нём остался импорт отсутствующего `app.domain.logging`.

### 4. Запустить приложение

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Откройте [ленту](http://localhost:8000) или [OpenAPI](http://localhost:8000/docs). Для административных страниц запустите Go отдельно по [инструкции](../admin-services/README.md#локальный-запуск) либо командой `docker compose up -d --build admin` после применения миграций.

## Основные маршруты

| Раздел | Маршруты |
| --- | --- |
| Лента | `GET /` |
| Регистрация | `GET /register`, `POST /auth/register` |
| Вход и выход | `GET /auth`, `POST /auth/login`, `GET /exit` |
| Публикация | `GET /article/submit`, `POST /article/submit/add` |
| Статья | `GET /article/{article_id}` |
| Редактирование | `GET /article/change/{article_id}`, `POST /article/change/{article_id}/access` |
| Удаление статьи | `POST /article/delete/{article_id}` |
| Реакции | `POST /article/{reaction}/{article_id}`, где `reaction` — `like` или `dislike` |
| Поиск | `GET /articles/search`, `GET /articles/search/title`, `GET /articles/search/category/{category}` |
| Комментарии | `POST /comments/{article_id}/create`, `POST /comments/{comment_id}/delete` |
| Профили | `GET /user/profile/{unique_username}` и разделы `/articles`, `/comments`, `/subscriptions`, `/liked` |
| Подписки | `POST /user/profile/{unique_username}/subscribe`, `POST /user/profile/{unique_username}/unsubscribe` |
| Удаление профиля | `GET /user/profile/{unique_username}/delete` |
| Администрирование | `/admin/login`, `/admin`, `/admin/users`, `/admin/articles`, `/admin/comments` |

Большая часть пользовательских маршрутов принимает формы и возвращает HTML или редиректы. Правило реакций — одна реакция на статью от пользователя за всё время, с уникальным ограничением PostgreSQL; ограничения «раз в день» в текущей реализации нет.

## Тесты и проверки

Тесты разделены на `tests/test_services`, `tests/test_repositories` и `tests/test_endpoints`. HTTP-тесты используют httpx и подмену зависимостей FastAPI; интеграционные тесты обращаются к PostgreSQL и Redis.

**Перед запуском полного набора тестов настройте изолированное окружение:**

- `TEST_DB_URL` должен вести в отдельную существующую тестовую БД: фикстура удаляет созданные таблицы после теста.
- `HOST_REDIS` и `PORT_REDIS` должны указывать на отдельный тестовый экземпляр Redis. Фикстура использует БД 1, но вызывает `FLUSHALL`, очищая **все базы этого Redis-сервера**. Смена номера БД не обеспечивает изоляцию.
- База `testmedhub` не создаётся через текущий `init.sql`. Создайте её отдельно, например `createdb -h localhost -U postgres testmedhub`, с пользователем и адресом своего тестового PostgreSQL.

Из `fastapi-app` с активированным окружением:

```bash
pytest
ruff check .
ruff format --check .
```

Отчёт покрытия Python-кода включён в настройки pytest. Эти команды описывают способ проверки; статус прохождения зависит от текущего состояния проекта и окружения.

Общие ограничения, включая незавершённую обработку просмотров и инвалидирование кеша после административных операций, перечислены в [главном README](../README.md#текущее-состояние-и-ограничения).
