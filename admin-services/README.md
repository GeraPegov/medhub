# MedHub Admin Service

HTTP-сервис на Go для административной части [MedHub](../README.md). Предоставляет защищённый JWT административный API, поиск и удаление записей, статистику за диапазон дат и Redis-лимитеры публикаций. HTML-интерфейс расположен в Python-приложении и обращается к сервису через HTTP.

## Стек и устройство

- Go 1.26.2, стандартный `net/http` и JSON.
- PostgreSQL через `pgx/pgxpool`, параметризованные SQL-запросы.
- Redis через `go-redis`: атомарные дневные и часовые счётчики.
- Интерфейсы между handler-, service- и storage-слоями.
- `context.Context` передаётся от HTTP-запроса до операций БД.
- JWT HS256 через `golang-jwt/jwt/v5`, bcrypt для паролей администраторов.
- Middleware `RequireAdmin` проверяет `Authorization: Bearer <token>`.
- Структурированные JSON-логи через `log/slog`.
- Четыре запроса статистики выполняются параллельно в горутинах с ожиданием через `sync.WaitGroup`.

Сервис использует общую с FastAPI базу `medhub`. Перед обращением к API необходимо применить миграции из `fastapi-app/alembic`; отдельных Go-миграций нет.

## Локальный запуск

Для запуска всего проекта используйте [Docker Compose](../README.md#быстрый-запуск). Для запуска Go-процесса на хосте потребуются Go 1.26.2, PostgreSQL с применёнными миграциями и Redis на `localhost:6379` для работы лимитеров.

Windows PowerShell:

```powershell
cd admin-services
Copy-Item cmd/.env.example .env
```

Linux / macOS:

```bash
cd admin-services
cp cmd/.env.example .env
```

Файл `.env` должен находиться в `admin-services`, поскольку конфигурация читается относительно рабочего каталога.

| Переменная | Назначение |
| --- | --- |
| `PROD_DB_URL` | PostgreSQL DSN, например `postgresql://postgres:change-me@localhost:5432/medhub` |
| `SECRET_KEY` | Секрет подписи административного JWT |

DSN Go-сервиса использует схему `postgresql://`; префикс `postgresql+asyncpg://` относится только к Python-приложению.

```bash
go mod download
go run ./cmd
```

Сервис слушает порт **8001**. Проверка сборки:

```bash
go build ./...
```

## Создание локального администратора

Учётная запись администратора отделена от обычного пользователя MedHub. После применения миграций и запуска Go-сервиса отправьте запрос регистрации.

PowerShell:

```powershell
$adminBody = @{
    login = 'local-admin'
    password = 'replace-with-a-strong-password'
} | ConvertTo-Json

Invoke-RestMethod -Method Post `
    -Uri 'http://localhost:8001/admin/register' `
    -ContentType 'application/json' `
    -Body $adminBody
```

Linux / macOS:

```bash
curl -X POST http://localhost:8001/admin/register \
  -H 'Content-Type: application/json' \
  -d '{"login":"local-admin","password":"replace-with-a-strong-password"}'
```

Успешная регистрация возвращает `201`. Затем откройте [форму входа FastAPI](http://localhost:8000/admin/login). `POST /admin/login` возвращает `access_token` и `token_type`; JWT действует 24 часа.

## HTTP API

| Метод | Путь | Назначение / параметры |
| --- | --- | --- |
| `POST` | `/admin/register` | Регистрация: JSON `login`, `password` |
| `POST` | `/admin/login` | Вход: JSON `login`, `password` |
| `GET` | `/admin/users` | Фильтры `user_id`, `email`, `username` |
| `DELETE` | `/admin/users/{id}` | Удаление пользователя |
| `GET` | `/admin/articles` | Фильтры `article_id`, `user_id`, `title`, `public_date` (`YYYY-MM-DD`) |
| `DELETE` | `/admin/articles/{id}` | Удаление статьи |
| `GET` | `/admin/comments` | Фильтры `article_id`, `user_id`, `public_date` (`YYYY-MM-DD`) |
| `DELETE` | `/admin/comments/{id}` | Удаление комментария |
| `GET` | `/admin/statistics` | Счётчики и топ-3 за полуинтервал `date_from <= created_at < date_to` |
| `POST` | `/limiter/{user_id}/articles` | Дневной лимит статей: `204` или `429` |
| `POST` | `/limiter/{user_id}/{article_id}/comments` | Часовой лимит комментариев: `204` или `429` |

Маршруты чтения и удаления `/admin/*` требуют Bearer-токен. Регистрация, вход и внутренние limiter-маршруты не проходят через `RequireAdmin`.

## Тесты

Тесты покрывают handler-, service- и storage-слои, включая JWT, лимитеры, фильтры, удаление и статистику. PostgreSQL-тесты читают `internal/storage/postgres/.env.tests` и очищают таблицы через `TRUNCATE`; Redis-тесты используют `localhost:6379` и удаляют созданные ключи.

Перед полным запуском подготовьте отдельную тестовую базу, укажите её в `TEST_DB_URL` и запустите Redis:

```bash
go test ./...
go vet ./...
```

Без Redis пакет `internal/storage/redis` завершится ошибкой подключения. Остальные пакеты можно проверить отдельно:

```bash
go test ./internal/handler ./internal/service ./internal/storage/postgres
```

## Ограничения текущей реализации

- `POST /admin/register` доступен без токена и предназначен только для локального или доверенного окружения.
- Redis-клиент использует жёстко заданный адрес `localhost:6379` и не назначает TTL ключам лимитера. В Docker-контейнере `localhost` не указывает на Compose-сервис Redis, поэтому Python-приложение переходит к SQL-проверке лимита. Старые ключи требуют отдельной очистки.
- Go-сервис напрямую изменяет PostgreSQL и пока не уведомляет Python-приложение об инвалидировании Redis-кеша.

Общие ограничения перечислены в [главном README](../README.md#текущее-состояние-и-ограничения).
