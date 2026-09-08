# MedHub Admin Service

HTTP-сервис на Go для административной части [MedHub](../README.md). Предоставляет поиск и удаление пользователей, статей и комментариев, а также статистику. HTML-интерфейс расположен в Python-приложении и обращается к сервису через HTTP.

## Стек и устройство

- Go 1.26.2, стандартный `net/http` и JSON.
- PostgreSQL через `pgx/pgxpool`, параметризованные SQL-запросы.
- Интерфейсы между обработчиками, сервисом и репозиторием административных операций.
- `context.Context` передаётся от HTTP-запроса в операции БД.
- JWT HS256 через `golang-jwt/jwt/v5`, bcrypt для паролей администраторов.
- Структурированные JSON-логи через `log/slog`.
- Четыре независимых запроса статистики выполняются в горутинах с ожиданием через `sync.WaitGroup`.

Сервис использует общую с FastAPI базу `medhub`. Перед обращением к API необходимо применить миграции из `fastapi-app/alembic`; отдельных Go-миграций нет.

## Локальный запуск

Для запуска всего проекта используйте [Docker Compose](../README.md#быстрый-запуск-через-docker-compose). Для запуска Go-процесса на хосте потребуются Go 1.26.2 и PostgreSQL с применёнными миграциями.

Из корня репозитория, Windows PowerShell:

```powershell
cd admin-services
Copy-Item cmd/.env.example .env
```

Linux / macOS:

```bash
cd admin-services
cp cmd/.env.example .env
```

Если `.env` уже существует, отредактируйте его без повторного копирования. Файл должен находиться в `admin-services/.env`: конфигурация читается относительно рабочего каталога.

| Переменная | Назначение |
| --- | --- |
| `PROD_DB_URL` | PostgreSQL DSN, например `postgresql://postgres:change-me@localhost:5432/medhub` |
| `SECRET_KEY` | Собственный секрет подписи JWT администратора |

DSN Go-сервиса использует схему `postgresql://`; префикс `postgresql+asyncpg://` относится только к Python-приложению.

После настройки `.env`, из `admin-services`:

```bash
go mod download
go run ./cmd
```

Сервис слушает порт **8001**. Для проверки сборки без запуска сервера:

```bash
go build ./...
```

Файлов `*_test.go` пока нет, поэтому `go test ./...` не подтверждает проверку бизнес-сценариев.

## Создание локального администратора

Учётная запись администратора отделена от обычного пользователя MedHub. После применения миграций и запуска Go-сервиса отправьте запрос регистрации. Ниже пример для PowerShell; замените логин и пароль своими значениями.

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

Для Linux / macOS:

```bash
curl -X POST http://localhost:8001/admin/register \
  -H 'Content-Type: application/json' \
  -d '{"login":"local-admin","password":"replace-with-a-strong-password"}'
```

Успешная регистрация возвращает `201`. Затем откройте [форму входа FastAPI](http://localhost:8000/admin/login). При прямом запросе к `POST /admin/login` сервис возвращает `access_token` и `token_type`; JWT действует 24 часа.

## HTTP API

| Метод | Путь | Назначение / параметры |
| --- | --- | --- |
| `POST` | `/admin/register` | Регистрация: JSON `login`, `password` |
| `POST` | `/admin/login` | Вход: JSON `login`, `password` |
| `GET` | `/admin/me` | Проверка `Authorization: Bearer <token>`; успех — `204`, ошибка — `401` |
| `GET` | `/admin/users` | Фильтры `user_id`, `email`, `username` |
| `DELETE` | `/admin/users/{id}` | Удаление пользователя |
| `GET` | `/admin/articles` | Фильтры `article_id`, `user_id`, `title` |
| `DELETE` | `/admin/articles/{id}` | Удаление статьи |
| `GET` | `/admin/comments` | Фильтры `article_id`, `user_id`, `public_date` (`YYYY-MM-DD`) |
| `DELETE` | `/admin/comments/{id}` | Удаление комментария |
| `GET` | `/admin/statistics` | Общие счётчики и выборки за `date` (`YYYY-MM-DD`) |

### Ограничения текущей реализации

Проверка JWT сейчас реализована в `/admin/me`, но не подключена ко всем маршрутам самого Go API. Проверка входа на HTML-страницах FastAPI не защищает прямые запросы к порту 8001. Регистрация администратора также доступна без токена. Используйте сервис только в доверенном локальном окружении; текущий Compose публикует этот порт на всех интерфейсах хоста.

Go-сервис напрямую изменяет PostgreSQL и пока не уведомляет Python-приложение об инвалидировании Redis-кеша. Подробнее — в [общем README](../README.md#текущее-состояние-и-ограничения).
